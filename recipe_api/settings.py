import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Try to import cloudinary, but don't crash if not available
try:
    import cloudinary

    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-default-dev-key-change-in-production"
)

# Set DEBUG to True for troubleshooting, then turn off later
DEBUG = True if os.environ.get("ENVIRONMENT") != "production" else False

# Update ALLOWED_HOSTS to include all possible domains during development
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,savora-recipe-b7493c60c573-2ac1db511588.herokuapp.com,savora-recipe-b7493c60c573.herokuapp.com",
).split(",")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "api",
]

# Add cloudinary apps only if available
if CLOUDINARY_AVAILABLE:
    INSTALLED_APPS.extend(["cloudinary_storage", "cloudinary"])

# Only add storages if AWS settings are configured
if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
    INSTALLED_APPS.append("storages")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add whitenoise for static files
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware must be before CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "recipe_api.urls"
WSGI_APPLICATION = "recipe_api.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Add error handling for database connection
try:
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
except Exception as e:
    print(f"Database configuration error: {str(e)}")
    # Fallback to SQLite in case of connection error
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Simplified static file serving.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Fix Media URL handling
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Add this section to serve media files in development
if DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Add these patterns to urlpatterns in urls.py
    MEDIA_URL_PATTERNS = static(MEDIA_URL, document_root=MEDIA_ROOT)

# Configure media storage for production only if AWS credentials are provided
if (
    not DEBUG
    and os.environ.get("AWS_ACCESS_KEY_ID")
    and os.environ.get("AWS_SECRET_ACCESS_KEY")
    and os.environ.get("AWS_STORAGE_BUCKET_NAME")
):
    # Setup S3 or other storage for production
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = "public-read"
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")

# CORS settings - Fix preflight issues
CORS_ALLOWED_ORIGINS = [
    "https://savora-recipe.netlify.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

# This is the critical fix - explicitly list all allowed headers
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_EXPOSE_HEADERS = ["*"]

# Add this for Heroku
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = ["https://savora-recipe.netlify.app"]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Rest Framework settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

# Configure static and media files for production
if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    # For media files in production
    if (
        os.environ.get("AWS_ACCESS_KEY_ID")
        and os.environ.get("AWS_SECRET_ACCESS_KEY")
        and os.environ.get("AWS_STORAGE_BUCKET_NAME")
    ):
        AWS_DEFAULT_ACL = "public-read"
        DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
        AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
        AWS_S3_SIGNATURE_VERSION = "s3v4"
        AWS_QUERYSTRING_AUTH = False
    else:
        # Temporary solution for Heroku's ephemeral filesystem
        # Warning: uploaded files will be lost on dyno restart
        MEDIA_ROOT = os.path.join(BASE_DIR, "media")
        MEDIA_URL = "/media/"

# Configure Django to use Cloudinary for media storage only if available
if CLOUDINARY_AVAILABLE:
    # Add Cloudinary settings
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME", "picture"),
        "API_KEY": os.environ.get("CLOUDINARY_API_KEY", "532336579731324"),
        "API_SECRET": os.environ.get(
            "CLOUDINARY_API_SECRET", "blu8Uz2x4iReT8qgmhJURF2N-QU"
        ),
    }
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    # Fallback to default file storage
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
