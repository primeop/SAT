from skyfield.api import load, EarthSatellite, wgs84, utc
import json
from datetime import datetime, timedelta
import numpy as np

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

def get_satellite_position(sat, timestamp):
    """Get satellite position at a given timestamp"""
    t = ts.from_datetime(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=utc))
    geo = sat.at(t).subpoint()
    return [geo.longitude.degrees, geo.latitude.degrees, geo.elevation.km * 1000]

# Load visibility data
with open('visibility_data.json', 'r') as f:
    visibility_data = json.load(f)

# Load TLEs
ts = load.timescale()
tles = {}
satellites = {}

with open('satellite_tles.txt', 'r') as f:
    tle_lines = f.readlines()

# Process TLE lines in pairs
for i in range(0, len(tle_lines), 2):
    tle1 = tle_lines[i].strip()
    tle2 = tle_lines[i + 1].strip()
    sat_id = tle1[2:7]
    satellites[sat_id] = EarthSatellite(tle1, tle2, f"Satellite_{sat_id}", ts)
    
    # Determine color based on inclination
    inclination = float(tle2[8:16])
    if inclination == 60:
        color = [0, 255, 0, 255]  # Green
    else:
        color = [0, 255, 255, 255]  # Cyan
    tles[sat_id] = {"tle1": tle1, "tle2": tle2, "color": color}

# Set up time parameters
start_time = datetime(2024, 5, 8, 0, 0, 0, tzinfo=utc)
end_time = start_time + timedelta(days=1)
interval_minutes = 5

# Create CZML document
czml = [
    {
        "id": "document",
        "name": "Satellite and LoS Visualization",
        "version": "1.0",
        "clock": {
            "interval": f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
            "currentTime": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "multiplier": 60,
            "range": "LOOP_STOP",
            "step": "SYSTEM_CLOCK_MULTIPLIER"
        }
    }
]

# Add ground stations to CZML
for station_id, station in ground_stations.items():
    czml.append({
        "id": f"GroundStation/{station_id}",
        "name": station["name"],
        "position": {
            "cartographicDegrees": [
                station["coordinates"][1],  # Longitude
                station["coordinates"][0],  # Latitude
                0  # Height (at ground level)
            ]
        },
        "billboard": {
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
            "scale": 0.5,
            "color": {
                "rgba": station["color"]
            }
        },
        "label": {
            "text": station["name"],
            "font": "12pt Roboto",
            "style": "FILL_AND_OUTLINE",
            "fillColor": {
                "rgba": station["color"]
            },
            "outlineColor": {
                "rgba": [0, 0, 0, 255]
            },
            "outlineWidth": 2
        }
    })

# Add satellites and their paths
model_url = "https://raw.githubusercontent.com/AnalyticalGraphicsInc/cesium-models/master/CesiumGround/Apps/SampleData/models/Satellite/Satellite.glb"

for sat_id, sat_data in tles.items():
    satellite = satellites[sat_id]
    points = []
    times = []
    
    # Generate satellite positions for the entire day
    current_time = start_time
    while current_time < end_time:
        t = ts.from_datetime(current_time)
        geo = satellite.at(t).subpoint()
        points.extend([current_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                      geo.longitude.degrees,
                      geo.latitude.degrees,
                      geo.elevation.km * 1000])
        times.append(current_time)
        current_time += timedelta(minutes=interval_minutes)

    # Add satellite to CZML
    czml.append({
        "id": f"Satellite/{sat_id}",
        "name": f"Satellite {sat_id}",
        "availability": f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "model": {
            "gltf": model_url,
            "scale": 500,
            "minimumPixelSize": 64
        },
        "label": {
            "text": f"SAT {sat_id}",
            "font": "12pt Roboto",
            "style": "FILL_AND_OUTLINE",
            "fillColor": {
                "rgba": sat_data["color"]
            },
            "outlineColor": {
                "rgba": [0, 0, 0, 255]
            },
            "outlineWidth": 2,
            "pixelOffset": {
                "cartesian2": [0, -30]
            }
        },
        "path": {
            "material": {
                "polylineOutline": {
                    "color": {
                        "rgba": sat_data["color"]
                    },
                    "outlineColor": {
                        "rgba": [0, 0, 0, 255]
                    },
                    "outlineWidth": 2
                }
            },
            "width": 2,
            "leadTime": 3600,
            "trailTime": 3600,
            "resolution": 120
        },
        "position": {
            "interpolationAlgorithm": "LAGRANGE",
            "interpolationDegree": 5,
            "referenceFrame": "INERTIAL",
            "epoch": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "cartographicDegrees": points
        }
    })

# Add Line of Sight visualizations
for station_id, station_data in visibility_data.items():
    station = ground_stations[station_id]
    station_position = [station["coordinates"][1], station["coordinates"][0], 0]
    
    for sat_id, visibility_windows in station_data.items():
        if not visibility_windows:
            continue
        
        # Create a single polyline entity for all visibility windows of this station-satellite pair
        los_points = []
        los_intervals = []
        
        for window in visibility_windows:
            timestamp = window["timestamp"]
            sat_position = get_satellite_position(satellites[sat_id], timestamp)
            
            # Add the visibility window to intervals
            los_intervals.append(f"{timestamp}/{timestamp}")
            
            # Add the line coordinates
            los_points.extend(station_position + sat_position)
        
        # Create the LoS visualization with intervals
        czml.append({
            "id": f"LoS/{station_id}/{sat_id}",
            "name": f"Line of Sight - {station['name']} to Satellite {sat_id}",
            "availability": los_intervals[0].split('/')[0] + "/" + los_intervals[-1].split('/')[-1],
            "polyline": {
                "positions": {
                    "cartographicDegrees": los_points
                },
                "material": {
                    "polylineGlow": {
                        "color": {
                            "rgba": station["color"]
                        },
                        "glowPower": 0.2,
                        "taperPower": 0.5
                    }
                },
                "width": 2
            }
        })

# Save the CZML file
with open('combined_visualization.czml', 'w') as f:
    json.dump(czml, f, indent=2)

print("Combined visualization has been saved to 'combined_visualization.czml'") 