import os
import sys
from pathlib import Path

# Add project root to Python path
path = Path(__file__).resolve().parent.parent
if str(path) not in sys.path:
    sys.path.insert(0, str(path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recipe_api.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
