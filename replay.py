import time
import hashlib

# Simulated secure command structure
def create_command(cmd_str, timestamp):
    token = hashlib.sha256((cmd_str + str(timestamp)).encode()).hexdigest()
    return {"command": cmd_str, "timestamp": timestamp, "token": token}

# Detection logic
def validate_command(received, current_time, time_window=60):
    expected_token = hashlib.sha256((received["command"] + str(received["timestamp"])).encode()).hexdigest()
    if received["token"] != expected_token:
        return False, "Token mismatch"
    if abs(current_time - received["timestamp"]) > time_window:
        return False, "Stale command (possible replay)"
    return True, "Valid"

# Original command
orig_cmd = create_command("SET_POWER_LOW", int(time.time()))
print("Sent command:", orig_cmd)

# Wait (simulate attacker replay)
time.sleep(5)  # Replace with longer time for stale/replay

# Replay attempt
valid, reason = validate_command(orig_cmd, int(time.time()))
print(f"Replay validation result: {valid} | Reason: {reason}")
