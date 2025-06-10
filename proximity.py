from skyfield.api import EarthSatellite, load
from geopy.distance import geodesic

# Time and satellite setup
ts = load.timescale()

# Victim Satellite (ISS)
line1_v = "1 25544U 98067A   24127.54791667  .00001764  00000+0  43262-4 0  9996"
line2_v = "2 25544  51.6448  81.1126 0004062 132.3403  38.2068 15.50620765393018"
victim = EarthSatellite(line1_v, line2_v, "Victim")

# Attacker Satellite - slightly adjusted orbit (very close inclination)
line1_a = "1 99999U 24001A   24127.54791667  .00001764  00000+0  50000-4 0  9990"
line2_a = "2 99999  52.1448  81.1126 0004062 132.3403  38.2068 15.50620765393018"  # only 0.5° difference
attacker = EarthSatellite(line1_a, line2_a, "Attacker")

# Simulate over 6 hours at 1-minute intervals
times = ts.utc(2024, 5, 7, 0, range(0, 360, 1))  # every 1 min for 6 hrs

log_file = open("proximity_log_extended.txt", "w")
log_file.write("Time,Distance_km\n")

# Proximity detection
for t in times:
    sp_v = victim.at(t).subpoint()
    sp_a = attacker.at(t).subpoint()
    coord_v = (sp_v.latitude.degrees, sp_v.longitude.degrees)
    coord_a = (sp_a.latitude.degrees, sp_a.longitude.degrees)
    distance_km = geodesic(coord_v, coord_a).km
    if distance_km < 300:  # looser threshold to capture more events
        log_line = f"{t.utc_iso()},{distance_km:.2f}\n"
        print(f"[PROXIMITY] {log_line.strip()}")
        log_file.write(log_line)

log_file.close()
