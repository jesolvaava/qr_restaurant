#!/bin/bash
set -o errexit

# Create required directories
mkdir -p media
mkdir -p staticfiles

# Install exact versions from requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Django deployment steps
python manage.py collectstatic --no-input
python manage.py migrate
