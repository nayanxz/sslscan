# SSL Scanner Expresspros

This project provides a Python-based GUI tool for scanning SSL/TLS configurations of websites using two popular tools: `testssl.sh` and `sslscan`. You can select domains from a list, choose the scanning method, and view the results of the SSL scans.

## Features
- **Domain Selection**: Select domains to scan using checkboxes or scan all domains in the list.
- **Two Scanning Methods**: Use either `testssl.sh` or `sslscan` for scanning SSL/TLS configurations.
- **Automatic Download and Setup**:
  - Automatically clones the `testssl.sh` repository if it's not present.
  - Automatically downloads and installs `sslscan` if it's not installed.
- **GUI Interface**: The user-friendly graphical interface makes it easy to choose domains and scanning methods.

## Prerequisites
- **Python 3.x**: The script requires Python 3 to run.
- **Dependencies**:
  - `requests`: To fetch domain lists from GitHub.
  - `gitpython`: To clone the `testssl.sh` repository.
  - `tkinter`: For the graphical user interface (usually bundled with Python).
  
To install the dependencies, use the following command:

```bash
pip install requests gitpython
