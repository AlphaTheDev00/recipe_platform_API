from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Make sure these imports are at the top
from api.views import health_check, api_root

urlpatterns = [
    # Root URL must come first
    path("", api_root, name="api_root"),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path("api/", include("api.urls")),
    path("health/", health_check, name="health_check"),
]

# Add static and media URL patterns in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
