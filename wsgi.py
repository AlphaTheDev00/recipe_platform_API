# This file should be removed as it's causing conflicts
# The correct WSGI file is in the recipe_api folder
import os
import sys
from pathlib import Path

# Redirecting to the proper WSGI file
from recipe_api.wsgi import application
