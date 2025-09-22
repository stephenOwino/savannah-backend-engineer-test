#!/bin/bash
set -e

cd /app/

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py createsuperuserifnotexists


