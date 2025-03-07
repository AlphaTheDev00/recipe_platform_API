from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Recipe, Ingredient, Rating, Comment, Favorite, Category
from .serializers import (
    UserSerializer,
    RecipeSerializer,
    IngredientSerializer,
    RatingSerializer,
    CommentSerializer,
    FavoriteSerializer,
    CategorySerializer,
)
from django.db.models import Avg, Q, Count, F
from django.utils import timezone
from datetime import timedelta
import os

# views

# This handles:
# User registration (creating new accounts)
# Getting user profile ( me endpoint)
# Updating profile information
# Viewing favorite recipes
# Viewing user ratings


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["POST"])
    def register(self, request):
        try:
            print("\n==== USER REGISTRATION DEBUG ====")
            print("Registering user with data:", request.data)

            # Check if database is accessible
            try:
                user_count = User.objects.count()
                print(f"Current user count: {user_count}")
            except Exception as db_err:
                print(f"Database check error during registration: {str(db_err)}")
                import traceback

                traceback.print_exc()
                return Response(
                    {"error": f"Database connection error: {str(db_err)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Check for existing user with same username
            username = request.data.get("username", "")
            if User.objects.filter(username=username).exists():
                print(f"Username '{username}' already exists!")
                return Response(
                    {"username": ["A user with that username already exists."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(data=request.data)
            print("Serializer initialized")

            if serializer.is_valid():
                print("Serializer is valid, saving user")
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                print(f"User registered successfully: {user.username} (ID: {user.pk})")
                return Response(
                    {"token": token.key, "user_id": user.pk, "email": user.email},
                    status=status.HTTP_201_CREATED,
                )

            print("Registration validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the error details
            print(f"Registration error: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"error": f"Server error: {str(e)}. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(
        detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(
        detail=False, methods=["PUT"], permission_classes=[permissions.IsAuthenticated]
    )
    def update_profile(self, request):
        """Update current user's profile"""
        # Handle multipart/form-data for profile picture uploads
        if request.content_type and "multipart/form-data" in request.content_type:
            # Extract profile data if it's in JSON format
            profile_data = {}
            if "profile" in request.data:
                try:
                    import json

                    profile_json = request.data.get("profile")
                    if isinstance(profile_json, str):
                        profile_data = json.loads(profile_json)
                except (ValueError, TypeError):
                    pass

            # Handle profile picture separately
            profile_picture = request.FILES.get("profile.profile_picture")
            if profile_picture:
                if not hasattr(request.user, "profile"):
                    UserProfile.objects.create(user=request.user)
                request.user.profile.profile_picture = profile_picture
                request.user.profile.save()

            # Update other profile fields if provided
            if profile_data:
                if not hasattr(request.user, "profile"):
                    UserProfile.objects.create(user=request.user, **profile_data)
                else:
                    for key, value in profile_data.items():
                        setattr(request.user.profile, key, value)
                    request.user.profile.save()

            # Update user fields
            user_data = {}
            for field in ["username", "email", "first_name", "last_name"]:
                if field in request.data:
                    user_data[field] = request.data.get(field)

            if user_data:
                for key, value in user_data.items():
                    setattr(request.user, key, value)
                request.user.save()

            # Return updated user data
            serializer = self.get_serializer(request.user, context={"request": request})
            return Response(serializer.data)
        else:
            # Handle regular JSON requests
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated]
    )
    def my_favorites(self, request):
        """Get current user's favorite recipes"""
        favorites = Recipe.objects.filter(favorites__user=request.user)
        serializer = RecipeSerializer(
            favorites,
            many=True,
            context={"request": request},  # Add this line to ensure is_favorited works
        )
        return Response(serializer.data)

    @action(
        detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated]
    )
    def my_ratings(self, request):
        """Get recipes rated by current user"""
        ratings = Rating.objects.filter(user=request.user)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)


# This helps organize recipes into categories like:
# Breakfast
# Dinner
# Desserts
# etc.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]


# Creating new recipes
# Viewing recipes with filters (by rating, ingredient, category, etc.)
# Updating recipes
# Deleting recipes
# Special features:
#  my_recipes: Shows recipes created by the current user
#  top_rated: Shows recipes with high ratings
#  recent: Shows newest recipes
#  similar_recipes: Finds recipes similar to a given one
#  recommendations: Suggests recipes based on user preferences
#  trending: Shows popular recipes based on recent activity


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "ingredients__name", "categories__name"]
    ordering_fields = ["created_at", "title", "cooking_time"]
    ordering = ["-created_at"]  # Default ordering

    def finalize_response(self, request, response, *args, **kwargs):
        # Add cache-busting headers to all responses
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

    def get_queryset(self):
        queryset = Recipe.objects.all().annotate(avg_rating=Avg("ratings__score"))

        # Filter by minimum rating
        min_rating = self.request.query_params.get("min_rating", None)
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=float(min_rating))

        # Filter by ingredient
        ingredient = self.request.query_params.get("ingredient", None)
        if ingredient:
            queryset = queryset.filter(ingredients__name__icontains(ingredient))

        # Filter by category name
        category = self.request.query_params.get("category", None)
        if category:
            queryset = queryset.filter(categories__name__icontains(category))

        # Filter by category ID
        category_id = self.request.query_params.get("category_id", None)
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        # Filter by difficulty
        difficulty = self.request.query_params.get("difficulty", None)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        # Filter by maximum cooking time
        max_time = self.request.query_params.get("max_cooking_time", None)
        if max_time:
            queryset = queryset.filter(cooking_time__lte=int(max_time))

        return queryset.distinct()  # Remove duplicates from OR queries

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        # Make sure request is always in context
        if "request" not in context and hasattr(self, "request"):
            context["request"] = self.request
        return context

    def handle_exception(self, exc):
        """
        Handle exceptions with better error responses
        """
        print(f"API Exception: {type(exc).__name__}: {str(exc)}")
        return super().handle_exception(exc)

    @action(detail=False, methods=["GET"])
    def my_recipes(self, request):
        """Get recipes created by the current user"""
        recipes = self.get_queryset().filter(author=request.user)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def top_rated(self, request):
        """Get top rated recipes"""
        recipes = self.get_queryset().filter(avg_rating__gte=4.0)[:10]
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def recent(self, request):
        """Get recently added recipes"""
        recipes = self.get_queryset().order_by("-created_at")[:10]
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"])
    def similar_recipes(self, request, pk=None):
        """Get similar recipes based on categories and ingredients"""
        try:
            recipe = self.get_object()

            # Initialize an empty queryset
            similar = Recipe.objects.none()

            # Add recipes with matching categories if the recipe has categories
            if recipe.categories.exists():
                category_matches = Recipe.objects.filter(
                    categories__in=recipe.categories.all()
                ).exclude(id=recipe.id)
                similar = similar | category_matches

            # Add recipes with matching ingredients if the recipe has ingredients
            if recipe.ingredients.exists():
                ingredient_matches = Recipe.objects.filter(
                    ingredients__name__in=recipe.ingredients.values_list(
                        "name", flat=True
                    )
                ).exclude(id=recipe.id)
                similar = similar | ingredient_matches

            if similar.exists():
                # Annotate with similarity score
                similar = (
                    similar.annotate(
                        category_matches=Count(
                            "categories",
                            filter=Q(categories__in=recipe.categories.all()),
                            distinct=True,
                        ),
                        ingredient_matches=Count(
                            "ingredients",
                            filter=Q(
                                ingredients__name__in=recipe.ingredients.values_list(
                                    "name", flat=True
                                )
                            ),
                            distinct=True,
                        ),
                    )
                    .annotate(
                        similarity_score=F("category_matches") + F("ingredient_matches")
                    )
                    .order_by("-similarity_score")[:5]
                )
            else:
                # If no similar recipes found, return recipes from the same author
                similar = (
                    Recipe.objects.filter(author=recipe.author)
                    .exclude(id=recipe.id)
                    .order_by("-created_at")[:5]
                )

            serializer = self.get_serializer(similar, many=True)
            return Response(serializer.data)

        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["GET"])
    def recommendations(self, request):
        """Get personalized recipe recommendations based on user's favorites and ratings"""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Get user's favorite categories from their rated and favorited recipes
        user_favorites = Recipe.objects.filter(
            Q(favorites__user=request.user)
            | Q(ratings__user=request.user, ratings__score__gte=4)
        )

        favorite_categories = Category.objects.filter(
            recipes__in=user_favorites
        ).distinct()

        # Get recipes in user's favorite categories, excluding ones they've already interacted with
        recommended = (
            Recipe.objects.filter(categories__in=favorite_categories)
            .exclude(Q(favorites__user=request.user) | Q(ratings__user=request.user))
            .annotate(avg_rating=Avg("ratings__score"))
            .filter(avg_rating__gte=4.0)
            .distinct()
            .order_by("-avg_rating", "-created_at")[:10]
        )

        serializer = self.get_serializer(recommended, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def trending(self, request):
        """Get trending recipes based on recent ratings, comments, and favorites"""
        # Get recipes with most interactions in the last 7 days
        last_week = timezone.now() - timedelta(days=7)
        trending = (
            Recipe.objects.filter(
                Q(ratings__created_at__gte=last_week)
                | Q(comments__created_at__gte=last_week)
                | Q(favorites__created_at__gte=last_week)
            )
            .annotate(
                interaction_count=Count("ratings")
                + Count("comments")
                + Count("favorites"),
                avg_rating=Avg("ratings__score"),
            )
            .filter(interaction_count__gt=0)
            .order_by("-interaction_count", "-avg_rating")[:10]
        )

        serializer = self.get_serializer(trending, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated]
    )
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status of a recipe for the current user"""
        recipe = self.get_object()
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()

        if favorite:
            favorite.delete()
            return Response(
                {"status": "unfavorited", "message": "Recipe removed from favorites"}
            )
        else:
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(
                {"status": "favorited", "message": "Recipe added to favorites"}
            )

    @action(detail=True, methods=["GET"])
    def favorite_status(self, request, pk=None):
        """Check if a recipe is favorited by the current user"""
        recipe = self.get_object()
        if not request.user.is_authenticated:
            return Response({"is_favorited": False})

        is_favorited = Favorite.objects.filter(
            user=request.user, recipe=recipe
        ).exists()
        return Response({"is_favorited": is_favorited})

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def update(self, request, *args, **kwargs):
        try:
            print("\n=== Recipe Update Debug ===")
            print(f"Request Method: {request.method}")
            print(f"Content-Type: {request.content_type}")

            # For multipart form data
            if request.content_type and "multipart/form-data" in request.content_type:
                # Fix difficulty case issue
                if "difficulty" in request.data:
                    difficulty = request.data.get("difficulty", "").lower()
                    request.data._mutable = True
                    request.data["difficulty"] = difficulty
                    request.data._mutable = False
                    # Convert difficulty to lowercase

                # Parse JSON strings in form data
                for field in ["ingredients", "categories"]:
                    if field in request.data:
                        try:
                            import json

                            if isinstance(request.data[field], str):
                                request.data._mutable = True
                                request.data[field] = json.loads(request.data[field])
                                request.data._mutable = False
                        except json.JSONDecodeError:
                            return Response(
                                {"error": f"Invalid {field} format"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

            # Debug the ingredients data
            print("\n=== Request Data Debug ===")
            for key, value in request.data.items():
                if key != "image":  # Skip image binary data
                    print(f"{key}: {value}")

            # Special debug for ingredients
            if "ingredients" in request.data:
                print("\n=== Ingredients Debug ===")
                ingredients_data = request.data.get("ingredients")
                print(f"Type: {type(ingredients_data)}")
                print(f"Value: {ingredients_data}")

                # Try to parse JSON if it's a string
                if isinstance(ingredients_data, str):
                    try:
                        import json

                        parsed = json.loads(ingredients_data)
                        print(f"Parsed JSON: {parsed}")
                        print(f"Parsed Type: {type(parsed)}")

                        # Modify request data to use parsed ingredients
                        if isinstance(parsed, list) and len(parsed) > 0:
                            request.data._mutable = True
                            request.data["ingredients"] = parsed
                            request.data._mutable = False
                            print("Successfully parsed and updated ingredients data")
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {str(e)}")

                # Ensure ingredients are included in the data for serializer
                if ingredients_data:
                    request.data._mutable = True
                    request.data["ingredients"] = ingredients_data
                    request.data._mutable = False
                    print(f"Added ingredients to request data: {ingredients_data}")

            # Create a copy of the request data to ensure all fields are included
            serializer_data = dict(request.data.items())

            # Ensure ingredients are included in the serializer data
            if "ingredients" in request.data:
                serializer_data["ingredients"] = request.data.get("ingredients")
                print(
                    f"Added ingredients to serializer data: {serializer_data['ingredients']}"
                )

            # Handle categories from form data (categories[0], categories[1], etc.)
            categories = []
            for key in request.data:
                if key.startswith("categories[") and key.endswith("]"):
                    categories.append(request.data.get(key))

            if categories:
                serializer_data["categories"] = categories
                print(f"Added categories to serializer data: {categories}")

            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=serializer_data, partial=True
            )
            if not serializer.is_valid():
                print("\n=== Validation Errors ===")
                for field, errors in serializer.errors.items():
                    print(f"{field}: {errors}")
                return Response(
                    {
                        "error": "Validation failed",
                        "details": serializer.errors,
                        "received_data": {
                            k: v for k, v in request.data.items() if k != "image"
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            recipe = serializer.save()

            # Safely serialize response to avoid image binary serialization issue
            response_data = self.get_serializer(recipe).data
            if "image" in response_data and not isinstance(response_data["image"], str):
                response_data["image"] = str(response_data["image"])

            return Response(
                {
                    "message": "Recipe updated successfully",
                    "recipe": response_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print("\n=== Exception Details ===")
            print(f"Type: {type(e)}")
            print(f"Args: {e.args}")
            print(f"Message: {str(e)}")
            import traceback

            print(traceback.format_exc())
            return Response(
                {"error": "Error processing request. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request, *args, **kwargs):
        try:

            # For multipart form data
            if request.content_type and "multipart/form-data" in request.content_type:
                # Fix difficulty case issue
                if "difficulty" in request.data:
                    difficulty = request.data.get("difficulty", "").lower()
                    request.data._mutable = True
                    request.data["difficulty"] = difficulty
                    request.data._mutable = False
                    print(f"Converted difficulty to: {request.data['difficulty']}")

                # Parse JSON strings in form data
                for field in ["ingredients", "categories"]:
                    if field in request.data:
                        try:
                            import json

                            if isinstance(request.data[field], str):
                                request.data._mutable = True
                                request.data[field] = json.loads(request.data[field])
                                request.data._mutable = False
                        except json.JSONDecodeError:
                            return Response(
                                {"error": f"Invalid {field} format"},
                                status=status.HTTP_400_BAD_REQUEST,
                            )

            # Debug the ingredients data
            print("\n=== Request Data Debug ===")
            for key, value in request.data.items():
                if key != "image":  # Skip image binary data
                    print(f"{key}: {value}")

            # Special debug for ingredients
            if "ingredients" in request.data:
                print("\n=== Ingredients Debug ===")
                ingredients_data = request.data.get("ingredients")
                print(f"Type: {type(ingredients_data)}")
                print(f"Value: {ingredients_data}")

                # Try to parse JSON if it's a string
                if isinstance(ingredients_data, str):
                    try:
                        import json

                        parsed = json.loads(ingredients_data)
                        print(f"Parsed JSON: {parsed}")
                        print(f"Parsed Type: {type(parsed)}")

                        # Modify request data to use parsed ingredients
                        if isinstance(parsed, list) and len(parsed) > 0:
                            request.data._mutable = True
                            request.data["ingredients"] = parsed
                            request.data._mutable = False
                            print("Successfully parsed and updated ingredients data")
                    except json.JSONDecodeError as e:
                        print(f"JSON Parse Error: {str(e)}")

                # Ensure ingredients are included in the data for serializer
                if ingredients_data:
                    request.data._mutable = True
                    request.data["ingredients"] = ingredients_data
                    request.data._mutable = False
                    print(f"Added ingredients to request data: {ingredients_data}")

            # Create a copy of the request data to ensure all fields are included
            serializer_data = dict(request.data.items())

            # Ensure ingredients are included in the serializer data
            if "ingredients" in request.data:
                serializer_data["ingredients"] = request.data.get("ingredients")
                print(
                    f"Added ingredients to serializer data: {serializer_data['ingredients']}"
                )

            # Handle categories from form data (categories[0], categories[1], etc.)
            categories = []
            for key in request.data:
                if key.startswith("categories[") and key.endswith("]"):
                    categories.append(request.data.get(key))

            if categories:
                serializer_data["categories"] = categories
                print(f"Added categories to serializer data: {categories}")

            serializer = self.get_serializer(data=serializer_data)
            if not serializer.is_valid():
                print("\n=== Validation Errors ===")
                for field, errors in serializer.errors.items():
                    print(f"{field}: {errors}")
                return Response(
                    {
                        "error": "Validation failed",
                        "details": serializer.errors,
                        "received_data": {
                            k: v for k, v in request.data.items() if k != "image"
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            recipe = serializer.save(author=request.user)

            # Safely serialize response to avoid image binary serialization issue
            response_data = self.get_serializer(recipe).data
            if "image" in response_data and not isinstance(response_data["image"], str):
                response_data["image"] = str(response_data["image"])

            return Response(
                {
                    "message": "Recipe created successfully",
                    "recipe": response_data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print("\n=== Exception Details ===")
            print(f"Type: {type(e)}")
            print(f"Args: {e.args}")
            print(f"Message: {str(e)}")
            import traceback

            print(traceback.format_exc())
            return Response(
                {"error": "Error processing request. Please try again."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False, methods=["POST"], permission_classes=[permissions.IsAuthenticated]
    )
    def batch_create(self, request):
        """Create multiple recipes at once"""
        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of recipes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_recipes = []
        errors = []

        for recipe_data in request.data:
            serializer = self.get_serializer(data=recipe_data)
            if serializer.is_valid():
                serializer.save(author=request.user)
                created_recipes.append(serializer.data)
            else:
                errors.append({"data": recipe_data, "errors": serializer.errors})

        return Response(
            {"created": created_recipes, "errors": errors},
            status=(
                status.HTTP_201_CREATED
                if created_recipes
                else status.HTTP_400_BAD_REQUEST
            ),
        )


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# Allows users to:
# Rate recipes (1-5 stars)
# View their ratings
# Update their ratings
# See average ratings for recipes


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Rating.objects.all()
        recipe_id = self.request.query_params.get("recipe", None)
        user_id = self.request.query_params.get("user", None)

        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["GET"])
    def user_rating(self, request):
        """Get a user's rating for a specific recipe"""
        recipe_id = request.query_params.get("recipe_id", None)
        if not recipe_id:
            return Response(
                {"error": "recipe_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        rating = Rating.objects.filter(user=request.user, recipe_id=recipe_id).first()

        if not rating:
            return Response(
                {"message": "No rating found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(rating)
        return Response(serializer.data)


# Enables users to:
# Add comments to recipes
# View comments on recipes
# Update/delete their own comments


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = Comment.objects.all().order_by("-created_at")
        recipe_id = self.request.query_params.get("recipe", None)
        if recipe_id:
            queryset = queryset.filter(recipe_id=recipe_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["GET"], permission_classes=[permissions.AllowAny])
    def recipe_comments(self, request):
        """Get comments for a specific recipe"""
        recipe_id = request.query_params.get("recipe_id", None)
        if not recipe_id:
            return Response(
                {"error": "recipe_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        comments = Comment.objects.filter(recipe_id=recipe_id).order_by("-created_at")
        serializer = self.get_serializer(
            comments, many=True, context={"request": request}
        )
        return Response(serializer.data)


# Allows users to:
# Mark recipes as favorites
# Remove recipes from favorites
# View their favorite recipes


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["POST"])
    def toggle(self, request):
        recipe_id = request.data.get("recipe_id")
        if not recipe_id:
            return Response(
                {"error": "recipe_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            recipe = Recipe.objects.get(id=recipe_id)
            favorite = Favorite.objects.filter(user=request.user, recipe=recipe).first()

            if favorite:
                favorite.delete()
                return Response(
                    {"message": "Recipe removed from favorites"},
                    status=status.HTTP_200_OK,
                )
            else:
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(
                    {"message": "Recipe added to favorites"},
                    status=status.HTTP_201_CREATED,
                )
        except Recipe.DoesNotExist:
            return Response(
                {"error": "Recipe not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Database check error: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"status": "error", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
def api_root(request):
    """Root endpoint providing API info and documentation"""
    return Response(
        {
            "name": "Savora Recipe API",
            "version": "1.0",
            "description": "REST API for managing recipes, ratings, comments and more",
            "endpoints": {
                "health_check": "/health/",
                "database_check": "/db-check/",
                "api_root": "/api/",
                "auth_token": "/api-token-auth/",
                "admin": "/admin/",
            },
        }
    )


@api_view(["GET"])
def health_check(request):
    """Health check endpoint to ensure the API is running"""
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def database_check(request):
    """Diagnostic endpoint to verify database connection"""
    try:
        # Simply check if we can run basic queries
        user_count = User.objects.count()
        recipe_count = Recipe.objects.count()
        category_count = Category.objects.count()

        # Get database URL for display purposes only
        db_url = os.environ.get("DATABASE_URL", "")
        db_host = "unknown"

        # Extract only the host part for security
        if "@" in db_url and "/" in db_url:
            parts = db_url.split("@")
            if len(parts) > 1:
                host_part = parts[1].split("/")[0]
                db_host = host_part

        return Response(
            {
                "status": "connected",
                "database_info": {
                    "user_count": user_count,
                    "recipe_count": recipe_count,
                    "category_count": category_count,
                    "database_host": db_host,
                },
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        print(f"Database check error: {str(e)}")
        import traceback

        traceback.print_exc()
        return Response(
            {"status": "error", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
