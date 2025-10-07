# Advanced Satellite Tracker: Real-Time Orbital Visualisation System

## A Python Flask application for tracking and visualising satellite passes with multiple plot types and orbital parameter analysis

---

## Overview

Advanced Satellite Tracker is a real-time satellite tracking application that calculates and visualises satellite positions relative to any observer location on Earth. Using the Skyfield astronomical library and live TLE data from CelesTrak, this application provides accurate predictions of satellite passes, orbital paths, and visibility windows.

The application automatically downloads current satellite data for space stations and weather satellites, performs high-precision orbital calculations, and generates multiple visualisation types including elevation plots, polar sky tracks, ground tracks, and velocity profiles. This tool is particularly useful for satellite observers, radio operators, and anyone interested in tracking visible satellite passes from their location.

### Key Features

- Real-time satellite data from CelesTrak (space stations and weather satellites)
- Multiple visualisation types: elevation, azimuth, distance, polar sky track, and ground track
- Automatic pass detection with rise and set times
- Orbital velocity calculations
- Observer location customisation
- Time range selection from 6 to 48 hours
- Detailed satellite information including inclination and altitude ranges
- Automatic port detection for hassle-free deployment
- Dark-themed responsive interface

---

## Application Screenshots

### Main Interface
![Main Dashboard](screenshots/tracker-dashboard.png)
*Control panel with satellite selection, plot type, observer location, and tracking duration*

### Elevation Plot
![Elevation Plot](screenshots/elevation-plot.png)
*Satellite elevation above horizon over time with pass annotations*

### Polar Sky Track
![Polar Track](screenshots/polar-track.png)
*Polar projection showing satellite paths across the sky*

### Ground Track
![Ground Track](screenshots/ground-track.png)
*Satellite ground track on world map with observer location*

### Distance and Velocity
![Distance Velocity](screenshots/distance-velocity.png)
*Distance from observer and orbital velocity analysis*

---

## Installation Instructions

### Prerequisites

Before installing, ensure you have the following installed on your system:
- Python 3.7 or higher
- pip (Python package manager)
- Internet connection (for downloading satellite data)

### Step 1: Download the Code

Save the provided code as `app.py` in your desired project directory.

### Step 2: Install Required Python Packages

Open a terminal or command prompt, navigate to your project directory, and run:
```bash
pip install flask matplotlib skyfield numpy pytz
```

This will install:

- Flask: Web framework for the application server
- Matplotlib: Plotting library for generating visualisations
- Skyfield: Astronomical calculations and satellite tracking
- NumPy: Numerical computing library
- pytz: Timezone handling

### Step 3: Verify Installation

You can verify the packages are installed correctly by running:
```bash
python -c "import flask, matplotlib, skyfield, numpy, pytz; print('All packages installed successfully')"
```

## Usage Instructions

### Starting the application

1. Open a terminal or command prompt
2. Navigate to the directory containing ```app.py```
3. Run the following command:
```bash
python app.py
```
4. You should see output similar to:
```bash
Starting Advanced Satellite Tracker...
Loading satellite data...
Ready! Open http://localhost:5000 in your browser
Or access from other devices: http://YOUR_IP_ADDRESS:5000
Press Ctrl+C to stop the server
```

Open your web browser and navigate to ```http://localhost:5000```

### Using the Application

#### Selecting a Satellite

The application provides several pre-loaded satellites organised by type:

#### Featured Satellites:

- ISS (ZARYA) - International Space Station
- TIANGONG - Chinese Space Station
- NOAA 15, 18, 19 - Polar Weather Satellites

Additional satellites are available in the dropdown menu below the separator line.

#### Setting Observer Location

Enter your location coordinates:

- Latitude: -90 to 90 degrees (negative for South, positive for North)
- Longitude: -180 to 180 degrees (negative for West, positive for East)

Default location is set to Western Australia (-20.3123, 118.64498).

#### Choosing Plot Type

Select from five visualisation types:

| Plot Type           | Description                                                   |
|---------------------|---------------------------------------------------------------|
| Elevation Over Time | Shows satellite elevation above horizon with pass annotations |
| Azimuth Direction   | Displays compass direction coloured by elevation              |
| Distance & Velocity | Shows distance from observer and orbital velocity             |
| Polar Sky Track     | Polar projection of satellite paths across the sky            |
| Ground Track        | Shows satellite ground track and observer location            |


#### Setting Time Range

Choose tracking duration:

- 6 hours
- 12 hours
- 24 hours (default)
- 48 hours

#### Generating Visualisation

Click the "Track Satellite" button to calculate positions and generate the plot. The application will:

1. Download latest TLE data if needed
2. Calculate satellite positions at optimal time intervals
3. Generate the selected plot type
4. Display the result in the browser


### Understanding the Visualisations

#### Elevation Plot

- Blue line: Satellite elevation above horizon
- Red dashed line: Horizon (0 degrees)
- Yellow dotted line: Good visibility threshold (10 degrees)
- Annotations: Pass details including maximum elevation and duration
- Cyan shading: Visible pass periods

#### Polar Sky Track

- Coloured lines: Individual satellite passes
- Triangle markers: Rise points (satellite appears)
- Inverted triangle markers: Set points (satellite disappears)
- Concentric circles: Elevation rings (30°, 60°, 90°)
- Compass labels: N, E, S, W directions

#### Ground Track

- Cyan line: Satellite path over Earth's surface
- Red star: Observer location
- Grid lines: Latitude and longitude reference

#### Distance & Velocity Plot

- Orange line: Distance from observer (left axis)
- Lime line: Orbital velocity (right axis)
- Red dotted lines: Typical altitude range for the satellite

#### Azimuth Plot

- Colour gradient: Elevation angle (purple = below horizon, yellow = high elevation)
- Compass labels: Cardinal directions at 0°, 90°, 180°, 270°

### Stopping the Application

To stop the server:

- Press ```Ctrl+C``` in the terminal where the application is running
- Wait for the shutdown message

## Technical Details

### Satellite Data Sources

The application automatically downloads TLE data from CelesTrak:

- Space Stations: https://celestrak.com/NORAD/elements/stations.txt
- Weather Satellites: https://celestrak.com/NORAD/elements/weather.txt

Data is cached during the session to minimise download requests.

### Calculation Methods

The application uses Skyfield for high-precision calculations:

- Position Calculation: SGP4 propagation from TLE data
- Observer Reference: Topocentric coordinates (altitude, azimuth, distance)
- Pass Detection: Automatic identification of rise and set events
- Time Resolution: Adaptive based on orbital period (typically 1-5 minute intervals)
- Velocity Calculation: Distance change between consecutive time steps

### Satellite Database

Pre-configured satellites with orbital characteristics:

| Satellite   | Type          | Inclination | Altitude Range | Orbital Period |
|-------------|---------------|-------------|----------------|----------------|
| ISS (ZARYA) | Space Station | 51.6°       | 370-460 km     | 92 minutes     |
| TIANGONG    | Space Station | 42.8°       | 350-450 km     | 91 minutes     |
| NOAA 15     | Weather       | 98.7°       | 800-850 km     | 101 minutes    |
| NOAA 18     | Weather       | 99.2°       | 850-870 km     | 102 minutes    |
| NOAA 19     | Weather       | 99.1°       | 870-880 km     | 102 minutes    |

### Port Configuration

The application automatically searches for available ports from 5000 to 5009. If all ports are in use, an error message will be displayed.

### Browser Compatibility

The application works on all modern browsers:

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### API Endpoints

| Method | Endpoint    | Description                                 |
|--------|-------------|---------------------------------------------|
| ```GET```    | ```/```           | Main application interface                  |
| ```GET```    | ```/satellites``` | Returns list of available satellites (JSON) |
| ```GET```    | ```/plot```       | Generates plot with query parameters        |

#### Query Parameters for /plot:

- ```satellite```: Satellite name
- ```latitude```: Observer latitude
- ```longitude```: Observer longitude
- ```hours```: Tracking duration
- ```plot_type```: Type of visualisation

## Troubleshooting

### Common Issues

#### Issue: Satellite data fails to load

Solution: Check internet connection. CelesTrak may be temporarily unavailable. Wait a few minutes and try again.

#### Issue: No visible passes shown

Solution: The satellite may not pass over your location during the selected time period. Try increasing the time range to 48 hours or select a different satellite. Polar-orbiting satellites (NOAA series) have better coverage than equatorial satellites.

#### Issue: Port already in use

Solution: The application will automatically try ports 5000-5009. If all are in use, close other applications or restart your computer.

#### Calculation takes too long

Solution: Longer time periods (48 hours) require more calculations. Wait for completion or reduce the time range.

#### Issue: Plot not displaying

Solution: Check browser console for errors. Ensure JavaScript is enabled. Try refreshing the page.

#### Issue: Location coordinates not updating

Solution: Ensure latitude is between -90 and 90, longitude between -180 and 180. Use decimal degrees format.

## File Structure
```bash
project-directory/
│
├── app.py                 # Main Flask application file
├── README.md             # This file
└── screenshots/          # (Optional) Directory for documentation images
    ├── tracker-dashboard.png
    ├── elevation-plot.png
    ├── polar-track.png
    ├── ground-track.png
    └── distance-velocity.png
```

## Project Architecture

### Frontend Components

- HTML Interface: Single-page application with dynamic form controls
- CSS Styling: Dark space-themed design with gradient effects
- JavaScript: Handles form submission, satellite loading, and plot updates
- AJAX Requests: Asynchronous data fetching without page reload

### Backend Components

- Flask Routes: Serves HTML and handles API requests
- Skyfield Library: Performs astronomical calculations and satellite propagation
- Matplotlib: Generates static plots with customised styling
- NumPy: Handles array operations for position and velocity calculations
- Caching System: Stores satellite data to reduce download requests

### Data Flow

1. User selects satellite and parameters
2. Frontend sends AJAX request to ```/plot``` endpoint
3. Backend calculates positions using Skyfield
4. Matplotlib generates plot as PNG image
5. Image encoded as base64 and returned to frontend
6. Browser displays image in plot container

## Understanding Satellite Tracking

### Observer Coordinates

#### Topocentric Coordinates:

- Altitude (Elevation): Angle above horizon (0° = horizon, 90° = directly overhead)
- Azimuth: Compass direction (0° = North, 90° = East, 180° = South, 270° = West)
- Distance: Straight-line distance from observer to satellite

### Satellite Passes

A satellite pass occurs when a satellite rises above the horizon, reaches maximum elevation, and sets below the horizon. Key parameters:

- Rise Time: When satellite appears above horizon
- Set Time: When satellite disappears below horizon
- Maximum Elevation: Highest point in the sky during pass
- Duration: Total time satellite is visible

#### Visibility Factors:

- Passes above 10° elevation are generally easier to observe
- Higher maximum elevations provide better viewing opportunities
- Night-time passes allow visual observation if satellite is illuminated

### Orbital Inclination

Inclination determines which latitudes a satellite can pass over:

- Low Inclination (0-30°): Limited to tropical and equatorial regions
- Medium Inclination (30-60°): Covers mid-latitude regions
- Polar Orbits (80-100°): Covers entire Earth over time

### TLE Data Format

Two-Line Element sets describe satellite orbits in a standardised format recognised by tracking software worldwide. The application automatically parses this data to calculate positions.

## Educational Use Cases

This application is ideal for:

- Amateur Satellite Observers: Planning observation sessions
- Radio Operators: Tracking communication satellites for contact opportunities
- Education: Teaching orbital mechanics and satellite technology
- Weather Monitoring: Understanding polar-orbiting weather satellite coverage
- Space Station Tracking: Finding ISS and Tiangong visible passes
- Photography: Planning satellite photography sessions

## Performance Notes

- Initial Load Time: 2-5 seconds for downloading satellite data
- Calculation Time: 1-3 seconds for 24-hour tracking period
- Memory Usage: Approximately 100-150 MB during operation
- Network Usage: Minimal after initial TLE download (cached for session)

## Satellite Visibility Tips

#### Best Viewing Conditions:

- Clear skies with minimal cloud cover
- Low light pollution for visual observations
- Passes with maximum elevation above 30°
- Dawn and dusk for illuminated satellites against dark sky

#### ISS Visibility:

- One of the brightest objects in night sky
- Visible to naked eye during favourable passes
- Multiple passes per day from most locations
- Best viewing during morning and evening twilight

#### Weather Satellites:

- Generally dimmer than ISS
- Require binoculars or telescope for visual observation
- Polar orbits provide regular coverage
- Useful for radio reception tracking

## Future Enhancements

Potential features for future versions:

- Real-time position updates with animation
- Pass prediction table with rise/set times
- Visibility calculations (daylight vs darkness)
- Multiple satellite comparison
- Radio frequency information for communication satellites
- Satellite footprint visualisation
- Export pass predictions to calendar
- Mobile-responsive touch controls
- Offline mode with cached TLE data

## Mathematical References

The tracking calculations are based on:

- Vallado, D. A., *"Fundamentals of Astrodynamics and Applications"*
- Hoots, F. R., Roehrich, R. L., *"Spacetrack Report No. 3: Models for Propagation of NORAD Element Sets"*
- Kelso, T. S., *"CelesTrak: Current NORAD Two-Line Element Sets"*

## License and Credits

This application uses the following open-source libraries:

| Library    | License              |
|------------|----------------------|
| Flask      | BSD-3-Clause License |
| Matplotlib | PSF-based License    |
| Skyfield   | MIT License          |
| NumPy      | BSD License          |
| pytz       | MIT License          |

Data Sources:

CelesTrak (Dr. T.S. Kelso) for TLE data

## Support and Contributions

For issues, questions, or suggestions:

1. Check the troubleshooting section above
2. Verify internet connection for TLE downloads
3. Ensure coordinates are in correct format
4. Try different time ranges if no passes are visible
5. Check browser console for JavaScript errors


## Version History

v1.0: Initial release with multiple plot types and automatic satellite data loading


## System Requirements

### Minimum Requirements

- Python 3.7+
- 2 GB RAM
- Internet connection for TLE data
- Modern web browser with JavaScript enabled

### Recommended

- Python 3.9+
- 4 GB RAM
- Stable internet connection
- Chrome or Firefox latest version

## Quick Start Example

For a quick test run:
```bash
# Install dependencies
pip install flask matplotlib skyfield numpy pytz

# Run application
python app.py

# Open browser to http://localhost:5000
```

Then:

1. Select "ISS (ZARYA)" from satellite dropdown
2. Keep default location or enter your coordinates
3. Select "Polar Sky Track" as plot type
4. Click "Track Satellite"
5. View the polar projection of ISS passes

## Acknowledgements

This application builds upon the excellent work of the astronomical Python community, particularly the Skyfield library by Brandon Rhodes. Special thanks to CelesTrak and Dr. T.S. Kelso for providing freely accessible satellite tracking data that makes applications like this possible.

## Made with Python, Flask, and a passion for Space Exploration.