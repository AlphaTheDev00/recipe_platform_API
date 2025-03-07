from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Recipe, Ingredient, Category, Rating, Comment, Favorite


class Command(BaseCommand):
    help = "Clear all data from the database except superusers"

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        Favorite.objects.all().delete()
        Rating.objects.all().delete()
        Comment.objects.all().delete()
        Ingredient.objects.all().delete()
        Recipe.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS("Database cleared successfully!"))
