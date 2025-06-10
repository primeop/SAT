from skyfield.api import EarthSatellite, load
import json
from datetime import datetime, timedelta

line1 = "1 10000U 25029BR  25128.63828704  .00001103  00000-0  33518-4 0  9998"
line2 = "2 10000  45.0000   0.7036 0003481   0.0000   0.3331 4.14466644  1776"
ts = load.timescale()
sat = EarthSatellite(line1, line2, "VirtualSat10000", ts)

czml = [{
    "id": "document",
    "name": "Virtual Satellite 10000",
    "version": "1.0"
}]

start_time = datetime(2024, 5, 8, 0, 0, 0)
points = []
intervals = []

for i in range(0, 90, 1):  # every minute for 90 mins
    t = ts.utc(2024, 5, 8, 0, i)
    geo = sat.at(t).subpoint()
    alt_km = sat.at(t).subpoint().elevation.km  
    timestamp = (start_time + timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
    points += [timestamp, geo.longitude.degrees, geo.latitude.degrees, alt_km * 1000]
    intervals.append(timestamp)

czml.append({
    "id": "Satellite/10000",
    "availability": f"{intervals[0]}/{intervals[-1]}",
    "label": {
        "text": "VirtualSat10000",
        "show": True
    },
    "path": {
        "material": {
            "polylineOutline": {
                "color": {"rgba": [255, 0, 0, 255]},
                "outlineColor": {"rgba": [0, 0, 0, 255]},
                "outlineWidth": 2
            }
        },
        "width": 2,
        "leadTime": 0,
        "trailTime": 3600,
        "resolution": 120
    },
    "position": {
        "interpolationAlgorithm": "LAGRANGE",
        "interpolationDegree": 5,
        "referenceFrame": "INERTIAL",
        "epoch": intervals[0],
        "cartographicDegrees": points
    }
})

with open("virtual_satellite_10000.czml", "w") as f:
    json.dump(czml, f, indent=2)
