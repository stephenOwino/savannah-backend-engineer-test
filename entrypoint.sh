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

# Create reviewer test account
echo "Setting up reviewer test account..."
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from api.models import Customer

if not User.objects.filter(username='reviewer').exists():
    user = User.objects.create_user(
        username='reviewer',
        email='reviewer@savannah.test',
        password='Review2024!'
    )
    Customer.objects.create(
        user=user,
        phone_number='+254700000000',
        address='Test Address, Nairobi'
    )
    print("✓ Reviewer account created")
else:
    print("✓ Reviewer account exists")
EOF

# Start Gunicorn
echo "Starting Gunicorn on port ${APP_PORT}..."
exec gunicorn --timeout 90 \
    --worker-tmp-dir /dev/shm \
    --workers 3 \
    --bind 0.0.0.0:${APP_PORT} \
    savannah_assess.wsgi:application
