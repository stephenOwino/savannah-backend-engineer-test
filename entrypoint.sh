#!/bin/bash
set -e

# Default port from environment, fallback to 8888
APP_PORT=${PORT:-8888}

cd /app/

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Ensure superuser exists
echo "Creating superuser if not exists..."
python manage.py createsuperuserifnotexists

# Load initial data (ignore errors if already loaded)
echo "Loading initial data fixtures..."
python manage.py loaddata api/fixtures/products.json || true

# Start Gunicorn
echo "Starting Gunicorn on port ${APP_PORT}..."
exec gunicorn --timeout 90 \
    --worker-tmp-dir /dev/shm \
    --workers 3 \
    --bind 0.0.0.0:${APP_PORT} \
    savannah_assess.wsgi:application
