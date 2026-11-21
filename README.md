
# Network Automation Toolkit

A Python-based network automation and monitoring toolkit designed to automate network device management, configuration backups, health monitoring, and alerting.

Built in a virtualized homelab environment using Proxmox VE, Ubuntu Server, Python, and a physical managed network switch.

## Project Overview

This project demonstrates how Python automation can reduce repetitive network administration tasks and improve network visibility.

The toolkit uses SSH to communicate with supported network devices, collects operational information, monitors connectivity, and generates reports.

## Key Features

- SSH network device management using Netmiko
- YAML-based network device inventory
- Automated collection of switch information
- Configuration backup functionality is not included in this public version
- Network connectivity monitoring using ICMP
- Device status change detection
- CSV reporting and activity logging
- Push notifications through ntfy
- Scheduled monitoring using systemd timers
- Automated report retention and log rotation

## Technologies Used

- Python 3
- Netmiko
- NAPALM
- PyYAML
- Ubuntu Server 24.04 LTS
- Proxmox VE
- SSH
- Linux systemd
- ntfy
- Git

## Architecture

The system consists of an Ubuntu Server virtual machine hosted on Proxmox.

The VM communicates with network devices over the management network.

The automation scripts perform device checks, collect information, and save reports locally.

A systemd timer runs network monitoring periodically.

When a device changes its response status, the system records the event and sends a push notification.

## Project Structure

- network_manager.py - Device automation and reporting
- network_monitor.py - ICMP connectivity monitoring
- change_detector.py - Status change detection and alerts
- network_watch.py - Monitoring workflow controller
- cleanup_reports.py - Automated report cleanup
- devices.example.yaml - Sample network device inventory
- health_targets.example.yaml - Sample monitoring inventory
- requirements.txt - Python dependencies

## Installation

Clone the repository and enter the project directory.

Create a Python virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Create local inventory files:

    cp devices.example.yaml devices.yaml
    cp health_targets.example.yaml health_targets.yaml

Edit the copied files with the addresses and settings for your own devices.

## Usage

Run switch automation:

    python network_manager.py

Run network health monitoring:

    python network_watch.py

Preview report cleanup:

    python cleanup_reports.py

Apply report retention rules:

    python cleanup_reports.py --apply

## Automated Monitoring

The homelab deployment uses systemd timers to run monitoring approximately every five minutes while the Ubuntu VM is powered on.

A separate daily timer handles report cleanup.

The service and timer configurations must be installed separately on the host operating system.

## Security Considerations

- Credentials are requested interactively rather than stored in the device inventory.
- Real device inventories and monitoring data are excluded from Git.
- Configuration backups are stored outside the public repository.
- Local report files use restricted filesystem permissions.
- Public ntfy topics should not be used to transmit sensitive information.
- Automation is intended for authorized devices and environments.

## Limitations

- Initial device automation has been tested with one physical TP-Link managed switch.
- ICMP monitoring determines responsiveness, not complete device health.
- Automated monitoring runs only while the Ubuntu VM is powered on.
- Some device drivers and CLI commands may require vendor-specific adjustments.

## Future Improvements

- Multi-vendor network automation
- Cisco switch integration
- VLAN configuration validation
- Network performance monitoring
- Web-based monitoring dashboard
- AI-assisted network troubleshooting
- Large-scale concurrent device monitoring

## Project Purpose

This project was developed to strengthen practical skills in network engineering, network security, Linux administration, Python programming, and infrastructure automation.

The long-term objective is to build automation solutions that can scale from a small homelab to larger enterprise network environments.
