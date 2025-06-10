from skyfield.api import load, EarthSatellite, wgs84, utc
from datetime import datetime, timedelta
import numpy as np
import json

# Ground station data
ground_stations = {
    "US_West": {
        "name": "Boardman, Oregon (USA)",
        "coordinates": [45.8397, -119.7006],
        "color": [255, 0, 0, 255]
    },
    "US_East": {
        "name": "Wallops Island (USA)",
        "coordinates": [37.9402, -75.4664],
        "color": [255, 165, 0, 255]
    },
    "Europe": {
        "name": "Dublin (Ireland)",
        "coordinates": [53.3331, -6.2489],
        "color": [255, 255, 0, 255]
    },
    "Asia_Pacific": {
        "name": "Sydney (Australia)",
        "coordinates": [-33.8688, 151.2093],
        "color": [148, 0, 211, 255]
    },
    "Middle_East": {
        "name": "Bahrain",
        "coordinates": [26.0667, 50.5577],
        "color": [0, 0, 255, 255]
    },
    "Africa": {
        "name": "Cape Town (South Africa)",
        "coordinates": [-33.9249, 18.4241],
        "color": [139, 69, 19, 255]
    }
}

def calculate_elevation_angle(satellite_position, ground_station_position, time):
    """
    Calculate elevation angle between a ground station and satellite
    Returns angle in degrees above horizon
    """
    # Convert ground station to geocentric position at the given time
    geocentric_station = ground_station_position.at(time)
    
    # Calculate topocentric position (relative to ground station)
    difference = satellite_position - geocentric_station
    alt, az, distance = difference.altaz()
    return alt.degrees

def is_visible(satellite_position, ground_station_position, time, min_elevation=10.0):
    """
    Determine if satellite is visible from ground station
    min_elevation: minimum elevation angle in degrees (default 10°)
    """
    elevation = calculate_elevation_angle(satellite_position, ground_station_position, time)
    return elevation > min_elevation

# Load TLEs
ts = load.timescale()
tles = {}

with open('satellite_tles.txt', 'r') as f:
    tle_lines = f.readlines()

# Process TLE lines in pairs
for i in range(0, len(tle_lines), 2):
    tle1 = tle_lines[i].strip()
    tle2 = tle_lines[i + 1].strip()
    sat_id = tle1[2:7]
    tles[sat_id] = [tle1, tle2]

# Create ground station objects
station_objects = {}
for station_id, station in ground_stations.items():
    lat, lon = station['coordinates']
    station_objects[station_id] = wgs84.latlon(lat, lon)

# Calculate visibility over time
start_time = datetime(2024, 5, 8, 0, 0, 0, tzinfo=utc)
duration_hours = 24
time_step_minutes = 5
visibility_data = {station_id: {} for station_id in ground_stations.keys()}

# Generate time points
time_points = []
for i in range(duration_hours * 60 // time_step_minutes):
    time = start_time + timedelta(minutes=i * time_step_minutes)
    time_points.append(ts.from_datetime(time))

# Calculate visibility for each satellite and ground station
print("Calculating Line of Sight visibility...")
for sat_id, (tle1, tle2) in tles.items():
    satellite = EarthSatellite(tle1, tle2, f"Satellite_{sat_id}", ts)
    
    for t in time_points:
        satellite_position = satellite.at(t)
        
        for station_id, station_position in station_objects.items():
            if station_id not in visibility_data:
                visibility_data[station_id] = {}
            if sat_id not in visibility_data[station_id]:
                visibility_data[station_id][sat_id] = []
            
            visible = is_visible(satellite_position, station_position, t)
            if visible:
                timestamp = t.utc_datetime().strftime("%Y-%m-%dT%H:%M:%SZ")
                elevation = calculate_elevation_angle(satellite_position, station_position, t)
                visibility_data[station_id][sat_id].append({
                    'timestamp': timestamp,
                    'elevation': elevation
                })

# Generate visibility report
print("\nVisibility Report:")
print("=================")

for station_id, station_data in visibility_data.items():
    print(f"\nGround Station: {ground_stations[station_id]['name']}")
    
    total_visible_time = 0
    max_gap = timedelta(0)
    
    for sat_id, visibility_windows in station_data.items():
        if visibility_windows:  # If there are visibility periods for this satellite
            print(f"\n  Satellite {sat_id}:")
            visible_time = len(visibility_windows) * time_step_minutes
            total_visible_time += visible_time
            
            # Print visibility windows
            for window in visibility_windows:
                print(f"    Time: {window['timestamp']}, Elevation: {window['elevation']:.1f}°")
            
            print(f"    Total visible time: {visible_time} minutes")

    print(f"\n  Total visibility time for all satellites: {total_visible_time} minutes")
    print(f"  Average visibility per day: {total_visible_time / duration_hours:.1f} minutes/hour")

# Save visibility data to JSON file
with open('visibility_data.json', 'w') as f:
    json.dump(visibility_data, f, indent=2)

print("\nVisibility data has been saved to 'visibility_data.json'") 