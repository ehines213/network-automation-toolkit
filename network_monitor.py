
import csv
import os
import subprocess
from datetime import datetime
from pathlib import Path

import yaml

os.umask(0o077)

# Load monitoring targets
with open("health_targets.yaml") as file:
    devices = yaml.safe_load(file)["devices"]

# Prepare report directory
report_dir = Path("reports")
report_dir.mkdir(exist_ok=True)
report_dir.chmod(0o700)

results = []
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print("=== NETWORK HEALTH MONITOR ===")

for device in devices:
    hostname = device["hostname"]
    ip = device["ip"]

    # Send two ICMP echo requests
    try:
        result = subprocess.run(
            ["ping", "-c", "2", "-W", "2", ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=8
        )
        status = "RESPONDING" if result.returncode == 0 else "NO RESPONSE"
    except subprocess.TimeoutExpired:
        status = "TIMEOUT"

    print(f"{hostname}: {status}")

    results.append({
        "timestamp": timestamp,
        "hostname": hostname,
        "ip_address": ip,
        "status": status
    })

# Save a CSV report
filename = report_dir / f"health_{timestamp}.csv"

with open(filename, "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["timestamp", "hostname", "ip_address", "status"]
    )
    writer.writeheader()
    writer.writerows(results)

responding = sum(
    1 for device in results
    if device["status"] == "RESPONDING"
)

print("\n=== SUMMARY ===")
print(f"Responding: {responding}")
print(f"Not responding: {len(devices) - responding}")
print(f"Report saved: {filename}")
