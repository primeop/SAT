from skyfield.api import EarthSatellite, load, wgs84
import matplotlib.pyplot as plt

# Load TLE for ISS (example)
line1 = "1 25544U 98067A   24127.54791667  .00001764  00000+0  43262-4 0  9996"
line2 = "2 25544  51.6448  81.1126 0004062 132.3403  38.2068 15.50620765393018"
satellite = EarthSatellite(line1, line2, "ISS (ZARYA)")

# Time range
ts = load.timescale()
times = ts.utc(2024, 5, 7, range(0, 90, 5))  # 0 to 90 mins, every 5 mins

# Compute ground positions
subpoints = [satellite.at(t).subpoint() for t in times]
lats = [sp.latitude.degrees for sp in subpoints]
lons = [sp.longitude.degrees for sp in subpoints]

# Plot ground track
plt.figure(figsize=(10, 5))
plt.plot(lons, lats, marker='o', linestyle='-', color='blue')
plt.title('ISS Ground Track over 90 Minutes')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True)
plt.tight_layout()
plt.show()
