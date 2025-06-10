from skyfield.api import EarthSatellite, load
import simplekml

# Load TLEs
ts = load.timescale()
kml = simplekml.Kml()

# Victim satellite (ISS)
line1_v = "1 25544U 98067A   24127.54791667  .00001764  00000+0  43262-4 0  9996"
line2_v = "2 25544  51.6448  81.1126 0004062 132.3403  38.2068 15.50620765393018"
victim = EarthSatellite(line1_v, line2_v, "Victim Satellite")

# Attacker satellite (modified inclination to simulate attacker orbit)
line1_a = "1 99999U 24001A   24127.54791667  .00001764  00000+0  50000-4 0  9990"
line2_a = "2 99999  56.6448  81.1126 0004062 132.3403  38.2068 15.50620765393018"
attacker = EarthSatellite(line1_a, line2_a, "Attacker Satellite")

# Generate coordinates for each
times = ts.utc(2024, 5, 7, range(0, 90, 5))
victim_coords = []
attacker_coords = []

for t in times:
    sp_v = victim.at(t).subpoint()
    sp_a = attacker.at(t).subpoint()
    victim_coords.append((sp_v.longitude.degrees, sp_v.latitude.degrees))
    attacker_coords.append((sp_a.longitude.degrees, sp_a.latitude.degrees))
    kml.newpoint(name=f"Victim-{t.utc_iso()}", coords=[(sp_v.longitude.degrees, sp_v.latitude.degrees)])
    kml.newpoint(name=f"Attacker-{t.utc_iso()}", coords=[(sp_a.longitude.degrees, sp_a.latitude.degrees)])

# Draw orbits
kml.newlinestring(name="Victim Orbit", coords=victim_coords).style.linestyle.color = simplekml.Color.green
kml.newlinestring(name="Attacker Orbit", coords=attacker_coords).style.linestyle.color = simplekml.Color.red

kml.save("two_satellites.kml")
