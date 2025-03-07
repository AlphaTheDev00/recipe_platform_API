import os
import django
import random
from django.contrib.auth import get_user_model

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_project.settings')
django.setup()

from api.models import Recipe, Category, Rating, Comment, Favorite
from django.db import connection

def reset_database():
    print("Deleting all existing data...")
    
    # Delete all data from related models first
    print("Deleting ratings...")
    Rating.objects.all().delete()
    
    print("Deleting comments...")
    Comment.objects.all().delete()
    
    print("Deleting favorites...")
    Favorite.objects.all().delete()
    
    print("Deleting recipes...")
    Recipe.objects.all().delete()
    
    print("Deleting categories...")
    Category.objects.all().delete()
    
    # Delete all users except superusers
    User = get_user_model()
    print("Deleting regular users...")
    User.objects.filter(is_superuser=False).delete()
    
    print("All data has been deleted.")
    
    # Reset sequences for PostgreSQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT setval(pg_get_serial_sequence('api_recipe', 'id'), 1, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('api_category', 'id'), 1, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('api_rating', 'id'), 1, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('api_comment', 'id'), 1, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('api_favorite', 'id'), 1, false);")
        cursor.execute("SELECT setval(pg_get_serial_sequence('auth_user', 'id'), (SELECT MAX(id) FROM auth_user), true);")
    
    print("Database sequences reset.")

if __name__ == "__main__":
    reset_database()
    print("Database has been reset. Run seed script to add new data.")
