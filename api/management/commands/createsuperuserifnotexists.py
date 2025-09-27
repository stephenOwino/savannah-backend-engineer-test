import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from api.models import Customer

User = get_user_model()


class Command(BaseCommand):
    """
    Custom management command to create a superuser and corresponding customer if they do not exist.
    Reads credentials from environment variables.
    """

    help = "Creates a superuser and customer if they do not already exist."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        # Optional: Add env vars for customer fields
        customer_phone = os.environ.get("DJANGO_CUSTOMER_PHONE", "1234567890")
        customer_address = os.environ.get("DJANGO_CUSTOMER_ADDRESS", "Admin Address")

        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR(
                    "Missing superuser credentials. Please set DJANGO_SUPERUSER_USERNAME, "
                    "DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD."
                )
            )
            return

        # Create superuser if it doesn't exist
        if not User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Creating superuser: {username}"))
            user = User.objects.create_superuser(username=username, email=email, password=password)
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' already exists."))
            user = User.objects.get(username=username)

        # Create customer if it doesn't exist
        if not Customer.objects.filter(user=user).exists():
            Customer.objects.create(user=user, phone_number=customer_phone, address=customer_address)
            self.stdout.write(self.style.SUCCESS(f"Created customer for {username}"))
        else:
            self.stdout.write(self.style.WARNING(f"Customer for {username} already exists"))
