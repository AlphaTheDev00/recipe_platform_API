import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import cloudinary
# Load environment variables from .env file
load_dotenv()nary.api

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(solve().parent.parent
    "SECRET_KEY", "django-insecure-default-dev-key-change-in-production"
) SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
# Set DEBUG to True temporarily to serve media files during development"
DEBUG = True

# Update ALLOWED_HOSTS to include all possible domainsuring development
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,savora-recipe-b7493c60c573-2ac1db511588.herokuapp.com,savora-recipe-b7493c60c573.herokuapp.com",
).split(",")S = os.environ.get(
    "ALLOWED_HOSTS",
# Application definition,savora-recipe-b7493c60c573-2ac1db511588.herokuapp.com,savora-recipe-b7493c60c573.herokuapp.com",
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",,
    "rest_framework",essions",
    "rest_framework.authtoken",
    "corsheaders",b.staticfiles",
    "api",framework",
]   "rest_framework.authtoken",
    "corsheaders",
# Only add storages if AWS settings are configured
if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
    INSTALLED_APPS.append("storages")
# Only add storages if AWS settings are configured
MIDDLEWARE = [get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add whitenoise for static files
    "corsheaders.middleware.CorsMiddleware",  # CORS middleware must be before CommonMiddleware
    "django.middleware.common.CommonMiddleware",re",
    "django.contrib.sessions.middleware.SessionMiddleware",itenoise for static files
    "django.middleware.csrf.CsrfViewMiddleware",CORS middleware must be before CommonMiddleware
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]   "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
# Required settings for Djangocking.XFrameOptionsMiddleware",
ROOT_URLCONF = "recipe_api.urls"
WSGI_APPLICATION = "recipe_api.wsgi.application"
# Required settings for Django
TEMPLATES = [= "recipe_api.urls"
    {APPLICATION = "recipe_api.wsgi.application"
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {django.template.backends.django.DjangoTemplates",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],  "django.template.context_processors.request",
        },      "django.contrib.auth.context_processors.auth",
    },          "django.contrib.messages.context_processors.messages",
]           ],
        },
# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Add error handling for database connection
try:tps://docs.djangoproject.com/en/5.1/ref/settings/#databases
    DATABASES = {
        "default": dj_database_url.config(on
            default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
            conn_max_age=600,
            conn_health_checks=True,onfig(
        )   default=os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3"),
    }       conn_max_age=600,
except Exception as e:h_checks=True,
    print(f"Database configuration error: {str(e)}")
    # Fallback to SQLite in case of connection error
    DATABASES = {as e:
        "default": { configuration error: {str(e)}")
            "ENGINE": "django.db.backends.sqlite3",r
            "NAME": BASE_DIR / "db.sqlite3",
        }default": {
    }       "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },ASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",alidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]   {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# Static files (CSS, JavaScript, Images)
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Simplified static file serving.to find static files.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Fix Media URL handling serving.
MEDIA_URL = "/media/" "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Fix Media URL handling
# Add this section to serve media files in development
if DEBUG:T = os.path.join(BASE_DIR, "media")
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
if DEBUG:
    # Add these patterns to urlpatterns in urls.py
    # This ensures media files are served properlyaticfiles_urlpatterns
    MEDIA_URL_PATTERNS = static(MEDIA_URL, document_root=MEDIA_ROOT)
    # Add these patterns to urlpatterns in urls.py
# Configure media storage for production only if AWS credentials are provided
if (MEDIA_URL_PATTERNS = static(MEDIA_URL, document_root=MEDIA_ROOT)
    not DEBUG
    and os.environ.get("AWS_ACCESS_KEY_ID")ly if AWS credentials are provided
    and os.environ.get("AWS_SECRET_ACCESS_KEY")
    and os.environ.get("AWS_STORAGE_BUCKET_NAME")
):  and os.environ.get("AWS_ACCESS_KEY_ID")
    # Setup S3 or other storage for production)
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
    AWS_S3_FILE_OVERWRITE = Falseviron.get("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_ACL = "public-read"viron.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN")-east-1")
    AWS_S3_FILE_OVERWRITE = False
# CORS settings_ACL = "public-read"
CORS_ALLOW_ALL_ORIGINS = Falseenviron.get("AWS_S3_CUSTOM_DOMAIN")
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")LL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = Trueiron.get(
CORS_ALLOW_METHODS = [INS", "http://localhost:3000,http://127.0.0.1:3000"
    "DELETE",
    "GET",_CREDENTIALS = True
    "OPTIONS",HODS = [
    "PATCH",,
    "POST",
    "PUT",NS",
]   "PATCH",
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization", [
    "content-type",
    "dnt",t-encoding",
    "origin",ation",
    "user-agent",",
    "x-csrftoken",
    "x-requested-with",
]   "user-agent",
    "x-csrftoken",
# Internationalization,
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = Trueization
USE_TZ = True = "en-us"
TIME_ZONE = "UTC"
# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Rest Framework settingsld type
REST_FRAMEWORK = { = "django.db.models.BigAutoField"
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],EFAULT_AUTHENTICATION_CLASSES": [
    "DEFAULT_PERMISSION_CLASSES": [ion.TokenAuthentication",
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}   "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
# Configure static and media files for production
if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
if not DEBUG:
    # For media files in productione.middleware.WhiteNoiseMiddleware")
    if (ICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
        os.environ.get("AWS_ACCESS_KEY_ID")
        and os.environ.get("AWS_SECRET_ACCESS_KEY")
        and os.environ.get("AWS_STORAGE_BUCKET_NAME")
    ):  os.environ.get("AWS_ACCESS_KEY_ID")
        AWS_DEFAULT_ACL = "public-read"ACCESS_KEY")
        DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
        AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
        AWS_S3_SIGNATURE_VERSION = "s3v4"
        AWS_QUERYSTRING_AUTH = Falseages.backends.s3boto3.S3Boto3Storage"
    else:WS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-1")
        # Temporary solution for Heroku's ephemeral filesystem
        # Warning: uploaded files will be lost on dyno restart
        MEDIA_ROOT = os.path.join(BASE_DIR, "media")
        MEDIA_URL = "/media/"for Heroku's ephemeral filesystem
        # Warning: uploaded files will be lost on dyno restart


















    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'    # Media files        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'    AWS_DEFAULT_ACL = 'public-read'    AWS_S3_FILE_OVERWRITE = False    AWS_S3_SIGNATURE_VERSION = 's3v4'    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')    # AWS S3 settings        INSTALLED_APPS += ['storages']if not DEBUG:# Configure S3 for media storage        MEDIA_ROOT = os.path.join(BASE_DIR, "media")
        MEDIA_URL = "/media/"

    # Cloudinary configuration
    INSTALLED_APPS += ['cloudinary_storage', 'cloudinary']






    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'    # Configure media storage to use cloudinary        }        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', '')    
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),