from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Creates demo users for the recipe platform'

    def handle(self, *args, **options):
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            Token.objects.get_or_create(user=admin)
            self.stdout.write(self.style.SUCCESS(f'Created admin user'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create demo users
        for i in range(1, 6):
            username = f"user{i}"
            email = f"user{i}@example.com"
            password = "password123"
            
            # Check if user already exists
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                # Create token for the user
                Token.objects.get_or_create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))
