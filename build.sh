#!/usr/bin/env bash
set -o errexit

# Create media directory if it doesn't exist
mkdir -p media

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate