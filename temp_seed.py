import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_PD5pumAbj9wl@ep-proud-field-abd59yrk-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require'
os.environ['DJANGO_SETTINGS_MODULE'] = 'recipe_api.settings'

import django
django.setup()

# Force clear ALL data including profiles
from django.contrib.auth.models import User
from api.models import Recipe, Category, Rating, Comment, Favorite, UserProfile, Ingredient

print('Clearing ALL data from database...')
Favorite.objects.all().delete()
Rating.objects.all().delete()
Comment.objects.all().delete()
Ingredient.objects.all().delete()
Recipe.objects.all().delete()
Category.objects.all().delete()
UserProfile.objects.all().delete()
User.objects.all().delete()  # Delete ALL users including superusers
print('Database completely cleared!')

from api.management.commands.seed_data import Command
cmd = Command()
options = {
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
    'clear': True
}
cmd.handle(**options)
