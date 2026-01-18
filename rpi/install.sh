#!/bin/bash
# Raspberry Pi system dependency
sudo apt install python3-picamera2
# Create a venv with system libraries
python -m venv venv --system-site-packages
# Activate the venv
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt