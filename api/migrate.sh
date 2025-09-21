#!/bin/bash
set -e

cd /app/

echo "Running migrations..."
/usr/local/bin/python manage.py migrate --noinput

echo "Creating superuser if not exists..."
/usr/local/bin/python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
email = "${DJANGO_SUPERUSER_EMAIL}"
password = "${DJANGO_SUPERUSER_PASSWORD}"

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print("Superuser created:", email)
else:
    print("ℹSuperuser already exists:", email)
EOF
