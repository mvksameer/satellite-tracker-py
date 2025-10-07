# Advanced Satellite Tracker - Real-Time Orbital Visualisation System

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
