#!/bin/bash
set -e

# Default port
APP_PORT=${PORT:-8888}

cd /app/

echo "Starting Gunicorn on port ${APP_PORT}..."
exec gunicorn --worker-tmp-dir /dev/shm \
    --workers 3 \
    --bind 0.0.0.0:${APP_PORT} \
    savannah_assess.wsgi:application

