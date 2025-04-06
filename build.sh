#!/bin/bash
set -o errexit

# Create required directories
mkdir -p media
mkdir -p staticfiles

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
