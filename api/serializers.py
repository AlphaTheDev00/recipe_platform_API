from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Recipe, Ingredient, Rating, Comment, Favorite, UserProfile, Category


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "bio",
            "favorite_cuisine",
            "cooking_experience",
            "profile_picture",
            "profile_picture_url",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"profile_picture": {"write_only": True, "required": False}}

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "profile",
            "profile_picture_url",
        )
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def get_profile_picture_url(self, obj):
        if hasattr(obj, "profile") and obj.profile.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile.profile_picture.url)
            return obj.profile.profile_picture.url
        return None

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", None)

        # Create user
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        # Create or update profile
        if profile_data:
            UserProfile.objects.update_or_create(user=user, defaults=profile_data)

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        password = validated_data.pop("password", None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if password:
            instance.set_password(password)

        instance.save()

        # Update profile if provided
        if profile_data:
            UserProfile.objects.update_or_create(user=instance, defaults=profile_data)

        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "created_at")
        extra_kwargs = {
            "name": {"validators": []},  # Remove unique validator
        }


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name")


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)
    author = UserSerializer(read_only=True)
    categories = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    category_details = CategorySerializer(
        source="categories", many=True, read_only=True
    )
    image_url = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "description",
            "instructions",
            "ingredients",
            "categories",
            "category_details",
            "author",
            "created_at",
            "updated_at",
            "cooking_time",
            "difficulty",
            "image",
            "image_url",
            "avg_rating",
            "is_favorited",
            "favorites_count",
        )
        extra_kwargs = {"image": {"write_only": True, "required": False}}

    def get_image_url(self, obj):
        if obj.image:
            return self.context["request"].build_absolute_uri(obj.image.url)
        return None

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, recipe=obj).exists()
        return False

    def get_favorites_count(self, obj):
        return obj.favorites.count()

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients", [])
        category_names = validated_data.pop("categories", [])
        recipe = Recipe.objects.create(**validated_data)

        # Handle ingredients
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        # Handle categories (can be IDs or names)
        for category_item in category_names:
            try:
                # Try to parse as integer (category ID)
                category_id = int(category_item)
                category = Category.objects.get(id=category_id)
                recipe.categories.add(category)
            except (ValueError, Category.DoesNotExist):
                # If not an integer or category not found, treat as name
                category, _ = Category.objects.get_or_create(
                    name=category_item, defaults={"description": ""}
                )
                recipe.categories.add(category)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        category_names = validated_data.pop("categories", None)

        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update ingredients if provided
        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(recipe=instance, **ingredient_data)

        # Update categories if provided
        if category_names is not None:
            instance.categories.clear()
            for category_item in category_names:
                try:
                    # Try to parse as integer (category ID)
                    category_id = int(category_item)
                    category = Category.objects.get(id=category_id)
                    instance.categories.add(category)
                except (ValueError, Category.DoesNotExist):
                    # If not an integer or category not found, treat as name
                    category, _ = Category.objects.get_or_create(
                        name=category_item, defaults={"description": ""}
                    )
                    instance.categories.add(category)

        return instance

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError("Cooking time must be positive")
        return value

    def validate(self, data):
        if "ingredients" not in data or not data["ingredients"]:
            raise serializers.ValidationError("At least one ingredient is required")
        if "categories" not in data or not data["categories"]:
            raise serializers.ValidationError("At least one category is required")
        return data


class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ("id", "recipe", "user", "score", "created_at")


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "recipe",
            "user",
            "profile_picture_url",
            "content",
            "created_at",
        )

    def get_profile_picture_url(self, obj):
        if hasattr(obj.user, "profile") and obj.user.profile.profile_picture:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.user.profile.profile_picture.url)
            return obj.user.profile.profile_picture.url
        return None


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ("id", "recipe", "user", "created_at")
