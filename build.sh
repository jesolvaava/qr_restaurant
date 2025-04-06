#!/bin/bash
set -o errexit

# Create required directories
mkdir -p /opt/render/project/src/media
mkdir -p /opt/render/project/src/staticfiles

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Django deployment steps
python manage.py collectstatic --no-input
python manage.py migrate

# Copy media files to Render's persistent storage
cp -r media/* /opt/render/project/src/media/ || true
