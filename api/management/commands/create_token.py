from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or get API token for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            token, created = Token.objects.get_or_create(user=user)
            
            action = "Created" if created else "Retrieved"
            self.stdout.write(self.style.SUCCESS(f'{action} token for {username}'))
            self.stdout.write(f'Token: {token.key}')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist'))