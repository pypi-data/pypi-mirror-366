# linsecure

**linsecure** is a lightweight CLI tool that scans a Linux system for basic security misconfigurations like SSH settings, open ports, outdated packages, and more.


## Features
- Detects weak SSH configurations
- Checks for firewall status
- Scans world-writable files and sudo misconfigs
- Generates clean `.txt` reports
- Easy to run: one command, zero setup

## ✅ Requirements

- Python **3.7+**
- **Linux** environment (Ubuntu, Debian, WSL, etc.)
## Installation

```bash
pip install linsecure

## Usage
python3 -m linsecure.cli --output ~/linsecure_report.txt





