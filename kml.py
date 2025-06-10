from skyfield.api import EarthSatellite, load
import simplekml

# ISS TLE
line1 = "1 25544U 98067A   24127.54791667  .00001764  00000+0  43262-4 0  9996"
line2 = "2 25544  51.6448  81.1126 0004062 132.3403  38.2068 15.50620765393018"
sat = EarthSatellite(line1, line2, "ISS (ZARYA)")

ts = load.timescale()
times = ts.utc(2024, 5, 7, range(0, 90, 5))

kml = simplekml.Kml()
coords = []

# Add points & collect coordinates for path
for t in times:
    sp = sat.at(t).subpoint()
    lat = sp.latitude.degrees
    lon = sp.longitude.degrees
    coords.append((lon, lat))  # KML uses (lon, lat) format
    kml.newpoint(name=str(t.utc_iso()), coords=[(lon, lat)])

# Add the path as a LineString
linestring = kml.newlinestring(name="ISS Orbit Path")
linestring.coords = coords
linestring.style.linestyle.width = 3
linestring.style.linestyle.color = simplekml.Color.red  # Red path

kml.save("iss_groundtrack.kml")
