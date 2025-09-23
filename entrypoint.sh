#!/bin/bash
set -e

# Default port
APP_PORT=${PORT:-8888}

cd /app/

# Load initial data (ignore errors if already loaded)
echo "Loading initial data fixtures..."
python manage.py loaddata api/fixtures/products.json || true

echo "Starting Gunicorn on port ${APP_PORT}..."
exec gunicorn --worker-tmp-dir /dev/shm \
    --workers 3 \
    --bind 0.0.0.0:${APP_PORT} \
    savannah_assess.wsgi:application

