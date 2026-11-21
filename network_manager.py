
import csv
import logging
import os
from datetime import datetime
from getpass import getpass
from pathlib import Path

import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException
)

# Make generated files private
os.umask(0o077)

# Create output directories
report_folder = Path("reports")
log_folder = Path("logs")

report_folder.mkdir(exist_ok=True)
log_folder.mkdir(exist_ok=True)

report_folder.chmod(0o700)
log_folder.chmod(0o700)

# Configure activity logging
logging.basicConfig(
    filename=log_folder / "network_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load network device inventory
with open("devices.yaml", "r") as file:
    inventory = yaml.safe_load(file)

devices = inventory["devices"]

password = getpass("Enter switch password: ")

results = []
successful = 0
failed = 0

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print("\n=== NETWORK AUTOMATION STARTED ===")

for device in devices:
    hostname = device["hostname"]
    ip = device["host"]

    print(f"\nConnecting to {hostname}...")

    connection_details = {
        "device_type": device["device_type"],
        "host": ip,
        "username": device["username"],
        "password": password
    }

    status = "FAILED"
    error_type = ""
    report_path = ""

    try:
        with ConnectHandler(**connection_details) as connection:
            filename = report_folder / f"{hostname}_{timestamp}.txt"

            with open(filename, "w") as report:
                for command in device["commands"]:
                    print(f"Running: {command}")

                    output = connection.send_command(command)

                    report.write(f"\n=== {command} ===\n")
                    report.write(output + "\n")

            status = "SUCCESS"
            report_path = str(filename)
            successful += 1

            print(f"[SUCCESS] {hostname}")
            logging.info(f"{hostname} ({ip}) - SUCCESS")

    except (NetmikoTimeoutException, NetmikoAuthenticationException) as error:
        error_type = type(error).__name__
        failed += 1

        print(f"[FAILED] {hostname}: {error_type}")
        logging.error(f"{hostname} ({ip}) - {error_type}")

    except Exception as error:
        error_type = type(error).__name__
        failed += 1

        print(f"[ERROR] {hostname}: {error_type}")
        logging.error(f"{hostname} ({ip}) - {error_type}")

    # Store results for the CSV report
    results.append({
        "hostname": hostname,
        "ip_address": ip,
        "status": status,
        "report": report_path,
        "error": error_type
    })

# Export execution summary to CSV
csv_filename = report_folder / f"summary_{timestamp}.csv"

with open(csv_filename, "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["hostname", "ip_address", "status", "report", "error"]
    )
    writer.writeheader()
    writer.writerows(results)

print("\n=== AUTOMATION SUMMARY ===")
print(f"Successful devices: {successful}")
print(f"Failed devices: {failed}")
print(f"Total devices: {len(devices)}")
print(f"\nCSV summary: {csv_filename}")
