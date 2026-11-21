
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Find the directory containing this script
project_dir = Path(__file__).resolve().parent

print("================================")
print("NETWORK MONITORING AUTOMATION")
print("================================")

print(f"Started: {datetime.now()}", flush=True)

# Step 1: Check device connectivity
print("\n[STEP 1] Checking network devices...", flush=True)

try:
    subprocess.run(
        [sys.executable, "network_monitor.py"],
        cwd=project_dir,
        check=True
    )

    # Step 2: Detect changes from previous results
    print("\n[STEP 2] Detecting status changes...", flush=True)

    subprocess.run(
        [sys.executable, "change_detector.py"],
        cwd=project_dir,
        check=True
    )

    print("\n[COMPLETE] Network monitoring finished successfully.")

except subprocess.CalledProcessError as error:
    print(f"\n[ERROR] Monitoring workflow failed: {error}")
    sys.exit(1)
