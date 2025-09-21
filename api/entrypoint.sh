#!/bin/bash
# Default port
APP_PORT=${PORT:-8000}

# Navigate to the app directory
cd /app/

# Start Gunicorn with Django project
exec gunicorn --worker-tmp-dir /dev/shm \
    --workers 3 \
    --bind 0.0.0.0:${APP_PORT} \
    django_k8s.wsgi:application
