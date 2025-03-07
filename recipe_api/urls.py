from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from api.views import health_check

urlpatterns = [
    # ...existing urlpatterns...
    path("health/", health_check, name="health_check"),
    # ...existing urlpatterns...
]
