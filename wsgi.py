# This file should be removed completely
# The correct wsgi.py is in the recipe_api folder
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipe_api.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
