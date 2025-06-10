import matplotlib.pyplot as plt
from datetime import datetime

timestamps = []
distances = []

# Read the log file
with open("proximity_log_extended.txt", "r") as f:
    next(f)  # skip header
    for line in f:
        time_str, distance = line.strip().split(",")
        timestamps.append(datetime.fromisoformat(time_str.replace("Z", "+00:00")))
        distances.append(float(distance))

# Plot proximity events
plt.figure(figsize=(10, 5))
plt.plot(timestamps, distances, marker='o', linestyle='-', color='red')
plt.axhline(100, color='gray', linestyle='--', label='Proximity Threshold (100km)')
plt.title("Satellite Proximity Events")
plt.xlabel("Time")
plt.ylabel("Distance (km)")
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("proximity_plot.png")
plt.show()
