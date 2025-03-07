from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import views

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'API is running'})

router = DefaultRouter()
router.register(r"recipes", views.RecipeViewSet)
router.register(r"ingredients", views.IngredientViewSet)
router.register(r"ratings", views.RatingViewSet)
router.register(r"comments", views.CommentViewSet)
router.register(r"favorites", views.FavoriteViewSet)
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"categories", views.CategoryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("health/", health_check, name="health_check"),
]
