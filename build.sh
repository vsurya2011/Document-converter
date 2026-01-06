#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

# Install the system tools needed for conversion
apt-get update
apt-get install -y libreoffice poppler-utils