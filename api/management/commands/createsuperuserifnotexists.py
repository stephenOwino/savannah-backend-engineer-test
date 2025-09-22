import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    """
    Custom management command to create a superuser if one does not exist.
    Reads credentials from environment variables.
    """
    help = 'Creates a superuser if one does not already exist.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not all([username, email, password]):
            self.stdout.write(self.style.ERROR(
                'Missing superuser credentials. Please set DJANGO_SUPERUSER_USERNAME, '
                'DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD.'
            ))
            return

        if not User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Creating superuser: {username}"))
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Superuser '{username}' already exists.")
            )
