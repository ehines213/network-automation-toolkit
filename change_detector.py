
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import quote

os.umask(0o077)

report_dir = Path("reports")
state_dir = Path("state")

report_dir.mkdir(exist_ok=True)
state_dir.mkdir(exist_ok=True)

report_dir.chmod(0o700)
state_dir.chmod(0o700)

state_file = state_dir / "device_status.json"
alert_file = report_dir / "status_alerts.csv"


def send_phone_alert(change):
    topic_file = (
        Path.home()
        / ".config/network-automation/ntfy_topic"
    )

    if not topic_file.exists():
        print("[WARNING] ntfy topic file missing.")
        return

    topic = topic_file.read_text().strip()

    if not topic:
        print("[WARNING] ntfy topic is empty.")
        return

    is_test = os.getenv("NETWORK_ALERT_TEST") == "1"

    title = (
        "TEST - Homelab Alert"
        if is_test
        else "Homelab Network Alert"
    )

    prefix = "[TEST] " if is_test else ""

    message = (
        f"{prefix}{change['hostname']}: "
        f"{change['previous_status']} -> "
        f"{change['current_status']}"
    )

    request = Request(
        f"https://ntfy.sh/{quote(topic, safe='')}",
        data=message.encode("utf-8"),
        headers={"Title": title},
        method="POST"
    )

    try:
        with urlopen(request, timeout=10):
            print(
                f"[NOTIFICATION SENT] {change['hostname']}"
            )
    except (URLError, TimeoutError) as error:
        print(
            f"[NOTIFICATION FAILED] "
            f"{type(error).__name__}"
        )


# Locate latest health report
reports = sorted(report_dir.glob("health_*.csv"))

if not reports:
    print("No health reports found.")
    raise SystemExit(1)

latest_report = reports[-1]

with open(latest_report, newline="") as file:
    rows = list(csv.DictReader(file))

if not rows:
    print("Health report is empty.")
    raise SystemExit(1)

current_status = {
    row["hostname"]: (
        "RESPONDING"
        if row["status"] == "RESPONDING"
        else "NO RESPONSE"
    )
    for row in rows
}

print("=== NETWORK STATUS CHANGE DETECTION ===")

if state_file.exists():
    with open(state_file) as file:
        previous_status = json.load(file)
else:
    previous_status = None

changes = []

if previous_status is None:
    print("Creating initial monitoring baseline.")
else:
    for hostname, new_status in current_status.items():
        old_status = previous_status.get(hostname)

        if old_status is None:
            print(f"[NEW DEVICE] {hostname}: {new_status}")

        elif old_status != new_status:
            print(
                f"[ALERT] {hostname}: "
                f"{old_status} -> {new_status}"
            )

            changes.append({
                "timestamp": datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                "hostname": hostname,
                "previous_status": old_status,
                "current_status": new_status
            })

        else:
            print(f"[OK] {hostname}: No change")

# Append any new alerts to history
if changes:
    new_file = (
        not alert_file.exists()
        or alert_file.stat().st_size == 0
    )

    with open(alert_file, "a", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "hostname",
                "previous_status",
                "current_status"
            ]
        )

        if new_file:
            writer.writeheader()

        writer.writerows(changes)

    print(f"\nSaved {len(changes)} alert(s) to {alert_file}")
    for change in changes:
        send_phone_alert(change)
else:
    print("\nNo new status changes detected.")

# Save the latest status for the next check
with open(state_file, "w") as file:
    json.dump(current_status, file, indent=4)

state_file.chmod(0o600)

print("Monitoring state updated.")
