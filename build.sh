#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python packages
pip install -r requirements.txt

# Install the actual software engines for PDF and Word
apt-get update && apt-get install -y libreoffice poppler-utils
