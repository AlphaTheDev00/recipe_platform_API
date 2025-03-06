from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'ratings', views.RatingViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'favorites', views.FavoriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 