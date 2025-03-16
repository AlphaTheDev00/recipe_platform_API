from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.apps import apps

class Command(BaseCommand):
    help = 'Resets the database and creates demo users'

    def handle(self, *args, **options):
        # Get all models
        all_models = apps.get_models()
        
        # Drop all tables
        with connection.cursor() as cursor:
            # Disable foreign key checks
            cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
            
            # Delete all data from all tables
            for model in all_models:
                if model._meta.app_label not in ['contenttypes', 'auth', 'sessions', 'admin']:
                    self.stdout.write(f'Deleting data from {model._meta.app_label}.{model.__name__}')
                    model.objects.all().delete()
            
            # Delete all users
            User.objects.all().delete()
            
            # Enable foreign key checks
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')
        
        # Create admin user
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        Token.objects.get_or_create(user=admin)
        self.stdout.write(self.style.SUCCESS(f'Created admin user'))
        
        # Create demo users
        for i in range(1, 6):
            username = f"user{i}"
            email = f"user{i}@example.com"
            password = "password123"
            
            user = User.objects.create_user(username=username, email=email, password=password)
            Token.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            
        self.stdout.write(self.style.SUCCESS('Database reset completed successfully'))
