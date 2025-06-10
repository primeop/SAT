from skyfield.api import load, EarthSatellite
import json
from datetime import datetime, timedelta

# Define colors for different orbital rings
ring_colors = {
    0: [0, 255, 0, 255],     # Green (60 degrees)
    1: [0, 255, 255, 255]    # Cyan (120 degrees)
}

# Define ground stations
ground_stations = {
    "US_West": {
        "name": "Boardman, Oregon (USA)",
        "coordinates": [45.8397, -119.7006],
        "color": [255, 0, 0, 255]  # Red
    },
    "US_East": {
        "name": "Wallops Island (USA)",
        "coordinates": [37.9402, -75.4664],
        "color": [255, 165, 0, 255]  # Orange
    },
    "Europe": {
        "name": "Dublin (Ireland)",
        "coordinates": [53.3331, -6.2489],
        "color": [255, 255, 0, 255]  # Yellow
    },
    "Asia_Pacific": {
        "name": "Sydney (Australia)",
        "coordinates": [-33.8688, 151.2093],
        "color": [148, 0, 211, 255]  # Purple
    },
    "Middle_East": {
        "name": "Bahrain",
        "coordinates": [26.0667, 50.5577],
        "color": [0, 0, 255, 255]  # Blue
    },
    "Africa": {
        "name": "Cape Town (South Africa)",
        "coordinates": [-33.9249, 18.4241],
        "color": [139, 69, 19, 255]  # Brown
    }
}

# Read TLEs from file
tles = {}
colors = {}

with open('satellite_tles.txt', 'r') as f:
    tle_lines = f.readlines()
    
# Process TLE lines in pairs
for i in range(0, len(tle_lines), 2):
    tle1 = tle_lines[i].strip()
    tle2 = tle_lines[i + 1].strip()
    
    # Extract satellite ID from TLE
    sat_id = tle1[2:7]
    
    # Determine ring based on inclination from TLE2
    inclination = float(tle2[8:16])
    if inclination == 60:
        ring = 0  # Green ring
    elif inclination == 120:
        ring = 1  # Cyan ring
    else:
        continue  # Skip satellites with 0 degree inclination
        
    tles[sat_id] = [tle1, tle2]
    colors[sat_id] = ring_colors[ring]

ts = load.timescale()
start_time = datetime(2024, 5, 8, 0, 0, 0)
czml = [{"id": "document", "name": "3D Satellites with Models", "version": "1.0"}]

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
            "outlineWidth": 2,
            "verticalOrigin": "BOTTOM",
            "horizontalOrigin": "LEFT",
            "pixelOffset": {
                "cartesian2": [10, 0]
            }
        }
    })

model_url = "https://raw.githubusercontent.com/AnalyticalGraphicsInc/cesium-models/master/CesiumGround/Apps/SampleData/models/Satellite/Satellite.glb"

for sat_id, (l1, l2) in tles.items():
    sat = EarthSatellite(l1, l2, f"Satellite_{sat_id}", ts)
    points = []
    for i in range(90):
        t = ts.utc(2024, 5, 8, 0, i)
        geo = sat.at(t).subpoint()
        timestamp = (start_time + timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        points += [timestamp, geo.longitude.degrees, geo.latitude.degrees, geo.elevation.km * 1000]

    color = colors[sat_id]
    czml.append({
        "id": f"Satellite/{sat_id}",
        "availability": f"{points[0]}/{points[-4]}",
        "label": {
            "text": f"SAT {sat_id}",
            "scale": 0.5,
            "fillColor": {"rgba": color},
            "outlineColor": {"rgba": [0, 0, 0, 255]},
            "outlineWidth": 1,
            "style": "FILL_AND_OUTLINE"
        },
        "model": {
            "gltf": model_url,
            "scale": 500,
            "minimumPixelSize": 64,
            "show": True
        },
        "path": {
            "material": {
                "polylineOutline": {
                    "color": {"rgba": color},
                    "outlineColor": {"rgba": [0, 0, 0, 255]},
                    "outlineWidth": 2
                }
            },
            "width": 2,
            "trailTime": 3600,
            "leadTime": 0,
            "resolution": 120
        },
        "position": {
            "interpolationAlgorithm": "LAGRANGE",
            "interpolationDegree": 5,
            "referenceFrame": "INERTIAL",
            "epoch": points[0],
            "cartographicDegrees": points
        }
    })

with open("czml_3d_satellites_with_models.json", "w") as f:
    json.dump(czml, f, indent=2)
