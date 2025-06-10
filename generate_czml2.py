from skyfield.api import load, EarthSatellite
import json
from datetime import datetime, timedelta

tles = {
    "37158": [
        "1 37158U 10045A   25129.34420285  .00000066  00000-0  00000+0 0  9992",
        "2 37158  43.6860 120.8264 0002618  10.1928  88.8241  0.87715737 52849"
    ],
    "42738": [
        "1 42738U 17028A   25126.19505183 -.00000271  00000-0  00000+0 0  9990",
        "2 42738  40.0600 249.0918 0738919 270.8307 271.6695  1.00245883 29045"
    ],
    "42917": [
        "1 42917U 17048A   25129.54996228 -.00000340  00000-0  00000+0 0  9994",
        "2 42917   0.0552 201.8578 0003451 215.1635 135.6135  1.00273342 28325"
    ],
    "42965": [
        "1 42965U 17062A   25128.49072770 -.00000347  00000-0  00000-0 0  9991",
        "2 42965  40.3480 348.6470 0746242 270.9296 282.7575  1.00263808 27754"
    ]
}

ts = load.timescale()
start_time = datetime(2024, 5, 8, 0, 0, 0)
czml = [{"id": "document", "name": "Multiple Satellites", "version": "1.0"}]

for sat_id, (line1, line2) in tles.items():
    sat = EarthSatellite(line1, line2, f"Satellite_{sat_id}", ts)
    points = []
    intervals = []
    for i in range(0, 90, 1):
        t = ts.utc(2024, 5, 8, 0, i)
        geo = sat.at(t).subpoint()
        alt_km = geo.elevation.km
        timestamp = (start_time + timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
        points += [timestamp, geo.longitude.degrees, geo.latitude.degrees, alt_km * 1000]
        intervals.append(timestamp)

    czml.append({
        "id": f"Satellite/{sat_id}",
        "availability": f"{intervals[0]}/{intervals[-1]}",
        "label": {
            "text": f"SAT {sat_id}",
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
            "trailTime": 3600,
            "leadTime": 0,
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

with open("multiple_satellites.czml", "w") as f:
    json.dump(czml, f, indent=2)
