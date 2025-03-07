from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

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
]
