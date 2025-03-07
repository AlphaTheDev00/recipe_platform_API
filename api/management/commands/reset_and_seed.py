from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Recipe, Ingredient, Category, Rating, Comment, Favorite, UserProfile
from api.management.commands.seed_data import Command as SeedCommand

class Command(BaseCommand):
    help = "Reset database and seed with 50 recipes"

    def handle(self, *args, **options):
        # Clear all data
        self.stdout.write("Clearing all existing data...")
        Favorite.objects.all().delete()
        Rating.objects.all().delete()
        Comment.objects.all().delete()
        Recipe.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Run seed command with 50 recipes
        seed_command = SeedCommand()
        seed_options = {
            'recipes': 50,
            'users': 10,
            'ratings': 100,
            'comments': 60,
            'favorites': 40,
            'verbosity': 1,
            'settings': None,
            'pythonpath': None,
            'traceback': False,
            'no_color': False,
            'force_color': False,
            'skip_checks': False,
            'clear': False
        }
        seed_command.handle(**seed_options)
        
        self.stdout.write(self.style.SUCCESS("Successfully reset and seeded database with 50 recipes!"))
