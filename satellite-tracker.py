from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for web
import io
import base64
from skyfield.api import load, Topos
import numpy as np
from pytz import timezone
import json
from datetime import datetime, timedelta
from urllib.parse import quote

app = Flask(__name__)

# Global variables for caching
satellites_cache = None
timescale = load.timescale()

# Satellite orbital characteristics database
SATELLITE_CHARACTERISTICS = {
    'ISS (ZARYA)': {
        'type': 'Space Station',
        'inclination': 51.6,
        'altitude_range': (370, 460),
        'period_minutes': 92,
        'description': 'International Space Station - 51.6° inclination'
    },
    'CSS (TIANHE)': {
        'type': 'Space Station',
        'inclination': 41.5,
        'altitude_range': (350, 450),
        'period_minutes': 91,
        'description': 'Chinese Space Station (Tianhe core module) - 41.5° inclination'
    },
    'NOAA 15': {
        'type': 'Weather Satellite',
        'inclination': 98.7,
        'altitude_range': (800, 850),
        'period_minutes': 101,
        'description': 'Polar Weather Satellite - 98.7° inclination'
    },
    'NOAA 18': {
        'type': 'Weather Satellite',
        'inclination': 99.2,
        'altitude_range': (850, 870),
        'period_minutes': 102,
        'description': 'Polar Weather Satellite - 99.2° inclination'
    },
    'NOAA 19': {
        'type': 'Weather Satellite',
        'inclination': 99.1,
        'altitude_range': (870, 880),
        'period_minutes': 102,
        'description': 'Polar Weather Satellite - 99.1° inclination'
    }
}

def load_satellites():
    """Load and cache satellite data"""
    global satellites_cache
    if satellites_cache is None:
        try:
            # celestrak's gp.php path is identical across queries (only the query
            # string differs), and skyfield's on-disk TLE cache keys off the URL
            # path alone, so every call below needs an explicit, distinct
            # filename or they'll all collide and silently reuse the first result.
            station_data = load.tle_file(
                'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle',
                filename='celestrak_stations.tle')
            weather_data = load.tle_file(
                'https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=tle',
                filename='celestrak_weather.tle')

            satellites_cache = {}
            for sat in station_data:
                satellites_cache[sat.name] = sat
            for sat in weather_data:
                satellites_cache[sat.name] = sat

            # Featured satellites can get reclassified out of their usual group
            # (e.g. retired NOAA payloads dropped from "weather") while still
            # having live TLEs. Fetch those by exact name as a fallback.
            missing = [name for name in SATELLITE_CHARACTERISTICS if name not in satellites_cache]
            for name in missing:
                try:
                    extra = load.tle_file(
                        f'https://celestrak.org/NORAD/elements/gp.php?NAME={quote(name)}&FORMAT=tle',
                        filename=f'celestrak_name_{quote(name, safe="")}.tle')
                    for sat in extra:
                        if sat.name == name:
                            satellites_cache[sat.name] = sat
                except Exception:
                    pass

        except Exception as e:
            print(f"Error loading satellites: {e}")
            satellites_cache = {}
    return satellites_cache

def get_satellite_positions(satellite_name, lat, lon, hours):
    """Calculate satellite positions for given parameters with improved orbital modeling"""
    satellites = load_satellites()
    if satellite_name not in satellites:
        return None, "Satellite not found"
    
    satellite = satellites[satellite_name]
    observer = Topos(latitude_degrees=float(lat), longitude_degrees=float(lon))
    
    #  satellite characteristics
    sat_info = SATELLITE_CHARACTERISTICS.get(satellite_name, {
        'type': 'Unknown',
        'inclination': 0,
        'altitude_range': (200, 2000),
        'period_minutes': 90,
        'description': f'{satellite_name} - Unknown orbit'
    })
    
    #  optimal time resolution based on orbital period
    period_minutes = sat_info['period_minutes']
    #time_resolution = max(1, period_minutes // 20)  # 20 points per orbit minimum
    time_resolution = 1

    # Time range with better resolution
    now = timescale.now()
    total_minutes = int(hours) * 60
    minutes = list(range(0, total_minutes, time_resolution))
    
    #  time array
    time_range = timescale.utc(
        now.utc_datetime().year, 
        now.utc_datetime().month,
        now.utc_datetime().day, 
        now.utc_datetime().hour, 
        [now.utc_datetime().minute + m for m in minutes]
    )
    
    #  positions
    orbit = (satellite - observer).at(time_range)
    altitude, azimuth, distance = orbit.altaz()
    
    #  additional orbital parameters
    geocentric = satellite.at(time_range)
    subpoint = geocentric.subpoint()
    lat_sat, lon_sat = subpoint.latitude.degrees, subpoint.longitude.degrees
    
    #  velocity and ground track
    velocity = []
    for i in range(len(time_range) - 1):
        dt = (time_range[i+1].tt - time_range[i].tt) * 24 * 3600  # seconds
        if dt > 0:
            #  positions at consecutive times
            pos1 = satellite.at(time_range[i])
            pos2 = satellite.at(time_range[i+1])
            dr = np.sqrt(sum((pos2.position.km - pos1.position.km)**2))
            velocity.append(dr / dt)
        else:
            velocity.append(0)
    velocity.append(velocity[-1] if velocity else 0)  # Duplicate last value
    
    return {
        'minutes': minutes,
        'altitude': altitude.degrees.tolist(),
        'azimuth': azimuth.degrees.tolist(),
        'distance': distance.km.tolist(),
        'velocity': velocity,
        'satellite_latitude': lat_sat.tolist(),
        'satellite_longitude': lon_sat.tolist(),
        'time_range': time_range,
        'satellite_name': satellite_name,
        'satellite_info': sat_info,
        'observer_lat': float(lat),
        'observer_lon': float(lon)
    }, None

def find_passes(altitude_data, azimuth_data, minutes, min_elevation=0):
    """Find satellite passes with proper rise/set detection"""
    passes = []
    altitude_array = np.array(altitude_data)
    azimuth_array = np.array(azimuth_data)
    minutes_array = np.array(minutes)
    
    # Find where satellite is above horizon
    above_horizon = altitude_array > min_elevation
    
    # Find transitions (rise/set points)
    transitions = np.where(np.diff(above_horizon.astype(int)))[0]
    
    # Group into passes
    if len(transitions) > 0:
        # If we start above horizon, add a start point
        if above_horizon[0]:
            transitions = np.insert(transitions, 0, 0)
        # If we end above horizon, add an end point
        if above_horizon[-1]:
            transitions = np.append(transitions, len(altitude_array) - 1)
        
        # Group into rise/set pairs
        for i in range(0, len(transitions) - 1, 2):
            start_idx = transitions[i]
            end_idx = transitions[i + 1] if i + 1 < len(transitions) else len(altitude_array) - 1
            
            if start_idx < end_idx:
                pass_data = {
                    'start_time': minutes_array[start_idx],
                    'end_time': minutes_array[end_idx],
                    'max_elevation': np.max(altitude_array[start_idx:end_idx+1]),
                    'duration': minutes_array[end_idx] - minutes_array[start_idx],
                    'start_az': azimuth_array[start_idx],
                    'end_az': azimuth_array[end_idx],
                    'indices': (start_idx, end_idx)
                }
                passes.append(pass_data)
    
    return passes

def create_plot(data, plot_type):
    """Generate plot based on type and return as base64 image"""
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sat_info = data['satellite_info']
    sat_name = data['satellite_name']
    
    if plot_type == 'altitude':
        ax.plot(data['minutes'], data['altitude'], 'cyan', linewidth=2, label='Elevation')
        ax.fill_between(data['minutes'], 0, data['altitude'], 
                       where=np.array(data['altitude']) > 0, alpha=0.3, color='cyan')
        
        ax.set_title(f"{sat_name}\nElevation Over Time - {sat_info['description']}", 
                    color='white', fontsize=14)
        ax.set_xlabel("Minutes from Now", color='white')
        ax.set_ylabel("Elevation (degrees)", color='white')
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Horizon')
        ax.axhline(y=10, color='yellow', linestyle=':', alpha=0.5, label='Good visibility')
        
        # Find and annotate passes
        passes = find_passes(data['altitude'], data['azimuth'], data['minutes'])
        for i, pass_data in enumerate(passes[:3]):  # Show first 3 passes
            ax.annotate(f'Pass {i+1}\nMax: {pass_data["max_elevation"]:.1f}°\nDur: {pass_data["duration"]:.1f}min',
                       xy=(pass_data['start_time'], pass_data['max_elevation']),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                       fontsize=8, color='black')
        
        ax.legend()
        ax.set_ylim(-10, 90)
        
    elif plot_type == 'azimuth':
        # Color code by elevation
        elevations = np.array(data['altitude'])
        colors = plt.cm.plasma((elevations + 10) / 100)  # Normalize for colormap
        
        scatter = ax.scatter(data['minutes'], data['azimuth'], c=elevations, 
                           cmap='plasma', s=20, alpha=0.8)
        plt.colorbar(scatter, ax=ax, label='Elevation (degrees)')
        
        ax.set_title(f"{sat_name}\nAzimuth Direction - {sat_info['description']}", 
                    color='white', fontsize=14)
        ax.set_xlabel("Minutes from Now", color='white')
        ax.set_ylabel("Azimuth (degrees)", color='white')
        ax.set_ylim(0, 360)
        
        # Add compass directions
        ax.set_yticks([0, 90, 180, 270, 360])
        ax.set_yticklabels(['N', 'E', 'S', 'W', 'N'])
        
    elif plot_type == 'distance':
        ax.plot(data['minutes'], data['distance'], 'orange', linewidth=2, label='Distance')
        
        # Add velocity on secondary axis
        ax2 = ax.twinx()
        ax2.plot(data['minutes'], data['velocity'], 'lime', linewidth=1, alpha=0.7, label='Velocity')
        ax2.set_ylabel("Velocity (km/s)", color='lime')
        ax2.tick_params(axis='y', labelcolor='lime')
        
        ax.set_title(f"{sat_name}\nDistance & Velocity - {sat_info['description']}", 
                    color='white', fontsize=14)
        ax.set_xlabel("Minutes from Now", color='white')
        ax.set_ylabel("Distance (km)", color='orange')
        
        # Add altitude range info
        alt_range = sat_info['altitude_range']
        ax.axhline(y=alt_range[0], color='red', linestyle=':', alpha=0.5, 
                  label=f'Min altitude (~{alt_range[0]} km)')
        ax.axhline(y=alt_range[1], color='red', linestyle=':', alpha=0.5,
                  label=f'Max altitude (~{alt_range[1]} km)')
        
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
    elif plot_type == 'polar':
        fig.clear()
        ax = fig.add_subplot(111, projection='polar')
        
        # Find passes
        passes = find_passes(data['altitude'], data['azimuth'], data['minutes'])
        
        colors = ['cyan', 'yellow', 'lime', 'orange', 'magenta']
        
        for i, pass_data in enumerate(passes):
            start_idx, end_idx = pass_data['indices']
            if start_idx < end_idx:
                # Convert to polar coordinates
                theta = np.radians(data['azimuth'][start_idx:end_idx+1])
                r = [90 - alt for alt in data['altitude'][start_idx:end_idx+1]]
                
                color = colors[i % len(colors)]
                ax.plot(theta, r, color=color, linewidth=2, 
                       label=f'Pass {i+1}: {pass_data["max_elevation"]:.1f}° max')
                
                # Mark start and end points
                ax.scatter(theta[0], r[0], c=color, s=50, marker='^', alpha=0.8)
                ax.scatter(theta[-1], r[-1], c=color, s=50, marker='v', alpha=0.8)
        
        # Customize polar plot
        ax.set_ylim(0, 90)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_title(f"{sat_name} - Sky Track\n{sat_info['description']}", 
                    color='white', fontsize=14, pad=20)
        
        # Add elevation rings
        ax.set_rticks([0, 30, 60, 90])
        ax.set_rgrids([30, 60, 90], ['60°', '30°', 'Zenith'], alpha=0.5)
        
        # Add compass directions
        ax.set_thetagrids([0, 90, 180, 270], ['N', 'E', 'S', 'W'])
        
        if passes:
            ax.legend(bbox_to_anchor=(1.1, 1.0), loc='upper left')
        else:
            ax.text(0, 45, 'No visible passes\nin selected time period', 
                   ha='center', va='center', fontsize=12, 
                   bbox=dict(boxstyle='round', facecolor='red', alpha=0.7))
    
    elif plot_type == 'ground_track':
        # Convert to numpy arrays for the wrap-around fix
        lons = np.array(data['satellite_longitude'])
        lats = np.array(data['satellite_latitude'])

        # Find where the longitude jumps across the map edge (difference > 300 degrees)
        diffs = np.diff(lons)
        wrap_indices = np.where(np.abs(diffs) > 300)[0]
        
        # Insert NaNs to tell Matplotlib to break the line
        lons_fixed = np.insert(lons, wrap_indices + 1, np.nan)
        lats_fixed = np.insert(lats, wrap_indices + 1, np.nan)

        # World map ground track using the fixed arrays
        ax.plot(lons_fixed, lats_fixed, 'cyan', linewidth=2, label='Ground track')
        ax.scatter(data['observer_lon'], data['observer_lat'], 
                  color='red', s=100, marker='*', label='Observer', zorder=5)
        
        # --- Keep all your original formatting below here ---
        ax.set_title(f"{sat_name}\nGround Track - {sat_info['description']}", 
                    color='white', fontsize=14)
        ax.set_xlabel("Longitude (degrees)", color='white')
        ax.set_ylabel("Latitude (degrees)", color='white')
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        ax.set_xticks(range(-180, 181, 60))
        ax.set_yticks(range(-90, 91, 30))
        ax.legend()
        
    ax.grid(True, alpha=0.3)
    ax.tick_params(colors='white')
    plt.tight_layout()
    
    # Convert plot to base64 string
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', facecolor='#1a1a1a', edgecolor='none', dpi=100)
    img_buffer.seek(0)
    img_string = base64.b64encode(img_buffer.read()).decode()
    plt.close()
    
    return img_string


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/tracker')
def tracker():
    return render_template('tracker.html')

@app.route('/roadmap')
def roadmap():
    return render_template('roadmap.html')

@app.route('/satellites')
def get_satellites():
    satellites = load_satellites()
    return jsonify(list(satellites.keys()))

@app.route('/plot')
def generate_plot():
    try:
        satellite_name = request.args.get('satellite')
        lat = request.args.get('latitude', '-20.3123')
        lon = request.args.get('longitude', '118.64498')
        hours = request.args.get('hours', '24')
        plot_type = request.args.get('plot_type', 'altitude')
        
        if not satellite_name:
            return jsonify({'error': 'Satellite name is required'})
        
        data, error = get_satellite_positions(satellite_name, lat, lon, hours)
        if error:
            return jsonify({'error': error})
        
        plot_image = create_plot(data, plot_type)
        return jsonify({'plot': plot_image})
        
    except Exception as e:
        return jsonify({'error': f'Calculation error: {str(e)}'})

def find_free_port():
    """Find a free port starting from 5000"""
    import socket
    for port in range(5000, 5010):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    return None

if __name__ == '__main__':
    print(" Starting Advanced Satellite Tracker...")
    print("Loading satellite data...")
    
    try:
        load_satellites()  # Preload satellites
        
        # Find a free port
        free_port = find_free_port()
        if free_port is None:
            print(" No free usable ports found between 5000-5009")
            print("Please close other applications or restart your computer")
            exit(1)
        
        print(f" Ready! Open http://localhost:{free_port} in your browser")
        print(f" Or access from other devices: http://YOUR_IP_ADDRESS:{free_port}")
        print("Press Ctrl+C to stop the server")
        
        app.run(debug=False, host='0.0.0.0', port=free_port, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n Advanced Satellite Tracker stopped. Goodbye!")
    except Exception as e:
        print(f" Error starting server: {e}")
        print("Try restarting your terminal or computer")