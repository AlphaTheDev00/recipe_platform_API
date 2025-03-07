# This file is causing confusion - should be removed
import os
from recipe_api.wsgi import application

# Make the application object directly available
application = application
