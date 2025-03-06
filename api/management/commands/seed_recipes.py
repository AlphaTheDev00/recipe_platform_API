import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Recipe, Category, Ingredient, Rating, Comment
from django.utils import timezone
from faker import Faker
import os
from django.conf import settings

fake = Faker()

# Sample recipe data
RECIPE_TITLES = [
    "Creamy Garlic Parmesan Pasta",
    "Spicy Thai Basil Chicken",
    "Classic Margherita Pizza",
    "Chocolate Chip Cookies",
    "Beef Stroganoff",
    "Vegetable Stir Fry",
    "Homemade Chicken Noodle Soup",
    "Grilled Salmon with Lemon Butter",
    "Mushroom Risotto",
    "Beef Tacos",
    "Vegetarian Lasagna",
    "Apple Pie",
    "Chicken Alfredo",
    "Shrimp Scampi",
    "Beef Bourguignon",
    "Vegetable Curry",
    "Lemon Blueberry Pancakes",
    "Roasted Vegetable Quinoa Bowl",
    "BBQ Pulled Pork",
    "Spinach and Feta Stuffed Chicken",
    "Honey Glazed Salmon",
    "Beef and Broccoli Stir Fry",
    "Vegetable Paella",
    "Chocolate Lava Cake",
    "Chicken Parmesan",
    "Shrimp Pad Thai",
    "Beef Enchiladas",
    "Vegetable Frittata",
    "Banana Bread",
    "Roasted Chicken with Vegetables",
]

INGREDIENTS_BY_CATEGORY = {
    "Italian": [
        "pasta",
        "tomatoes",
        "garlic",
        "basil",
        "olive oil",
        "parmesan cheese",
        "mozzarella",
        "oregano",
        "bell peppers",
        "onions",
    ],
    "Pasta": [
        "spaghetti",
        "fettuccine",
        "penne",
        "linguine",
        "garlic",
        "olive oil",
        "parmesan",
        "cream",
        "tomato sauce",
        "basil",
    ],
    "Breakfast": [
        "eggs",
        "bacon",
        "bread",
        "butter",
        "maple syrup",
        "flour",
        "milk",
        "sugar",
        "baking powder",
        "berries",
    ],
    "Lunch": [
        "bread",
        "lettuce",
        "tomato",
        "cheese",
        "ham",
        "turkey",
        "mayonnaise",
        "mustard",
        "avocado",
        "cucumber",
    ],
    "Dinner": [
        "chicken",
        "beef",
        "rice",
        "potatoes",
        "broccoli",
        "carrots",
        "onions",
        "garlic",
        "olive oil",
        "salt",
    ],
    "Dessert": [
        "flour",
        "sugar",
        "butter",
        "eggs",
        "vanilla extract",
        "chocolate chips",
        "baking powder",
        "milk",
        "cream",
        "berries",
    ],
    "Appetizer": [
        "cheese",
        "crackers",
        "olives",
        "dip",
        "chips",
        "vegetables",
        "bread",
        "olive oil",
        "garlic",
        "herbs",
    ],
    "Snack": [
        "nuts",
        "chips",
        "popcorn",
        "pretzels",
        "fruit",
        "yogurt",
        "granola",
        "chocolate",
        "crackers",
        "cheese",
    ],
    "Soup": [
        "broth",
        "vegetables",
        "meat",
        "noodles",
        "beans",
        "herbs",
        "onions",
        "garlic",
        "carrots",
        "celery",
    ],
    "Salad": [
        "lettuce",
        "tomatoes",
        "cucumber",
        "dressing",
        "cheese",
        "croutons",
        "onions",
        "peppers",
        "olives",
        "avocado",
    ],
    "Beverage": [
        "water",
        "milk",
        "juice",
        "coffee",
        "tea",
        "soda",
        "alcohol",
        "sugar",
        "lemon",
        "ice",
    ],
    "Baking": [
        "flour",
        "sugar",
        "butter",
        "eggs",
        "baking powder",
        "vanilla extract",
        "salt",
        "milk",
        "chocolate",
        "nuts",
    ],
}

INSTRUCTIONS_TEMPLATES = [
    "1. Prepare all ingredients.\n2. {step1}\n3. {step2}\n4. {step3}\n5. Serve and enjoy!",
    "1. Preheat the oven to {temp}°F.\n2. {step1}\n3. {step2}\n4. Bake for {time} minutes.\n5. {step3}\n6. Let cool before serving.",
    "1. Heat oil in a large pan.\n2. {step1}\n3. {step2}\n4. {step3}\n5. Season with salt and pepper to taste.\n6. Serve hot.",
    "1. Boil water in a large pot.\n2. {step1}\n3. {step2}\n4. Drain and set aside.\n5. {step3}\n6. Combine all ingredients and serve.",
    "1. Mix all dry ingredients in a bowl.\n2. {step1}\n3. {step2}\n4. {step3}\n5. Let rest for {time} minutes before serving.",
]

COOKING_STEPS = [
    "Chop all vegetables into small pieces.",
    "Mix the sauce ingredients together in a small bowl.",
    "Sauté the onions and garlic until fragrant.",
    "Add the meat and cook until browned.",
    "Stir in the vegetables and cook until tender.",
    "Pour in the sauce and bring to a simmer.",
    "Add the spices and herbs.",
    "Cover and cook on low heat for 15 minutes.",
    "Stir occasionally to prevent sticking.",
    "Add the cheese and stir until melted.",
    "Fold in the whipped cream gently.",
    "Knead the dough until smooth and elastic.",
    "Roll out the dough on a floured surface.",
    "Layer the ingredients in the baking dish.",
    "Marinate the meat for at least 30 minutes.",
    "Grill on each side for 5 minutes.",
    "Roast in the oven until golden brown.",
    "Blend until smooth and creamy.",
    "Garnish with fresh herbs before serving.",
    "Refrigerate for at least 2 hours before serving.",
]

DESCRIPTIONS = [
    "A delicious {category} recipe that's perfect for {meal}. This {adjective} dish is sure to impress your family and friends.",
    "This {adjective} {category} recipe is a family favorite. It's perfect for {meal} and takes only {time} minutes to prepare.",
    "A classic {category} dish with a modern twist. This {adjective} recipe is perfect for {meal} and special occasions.",
    "Quick and easy {category} recipe that's perfect for busy weeknights. This {adjective} dish is ready in just {time} minutes.",
    "A hearty {category} dish that's full of flavor. This {adjective} recipe is perfect for {meal} and will satisfy even the pickiest eaters.",
]

ADJECTIVES = [
    "delicious",
    "mouthwatering",
    "tasty",
    "flavorful",
    "savory",
    "delightful",
    "scrumptious",
    "appetizing",
    "delectable",
    "luscious",
]
MEALS = [
    "breakfast",
    "lunch",
    "dinner",
    "a quick snack",
    "a special occasion",
    "weeknight meals",
    "weekend brunches",
    "holiday gatherings",
]


class Command(BaseCommand):
    help = "Seeds the database with sample recipes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=30, help="Number of recipes to create"
        )
        parser.add_argument("--user", type=str, help="Username to assign recipes to")

    def handle(self, *args, **options):
        count = options["count"]
        username = options["user"]

        # Get or create user
        if username:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user {username}"))
        else:
            # Get the first user or create a new one
            if User.objects.exists():
                user = User.objects.first()
            else:
                user = User.objects.create_user(
                    username="admin", email="admin@example.com", password="password123"
                )
                self.stdout.write(self.style.SUCCESS("Created admin user"))

        # Get all categories
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(
                self.style.WARNING(
                    "No categories found. Creating default categories..."
                )
            )
            for category_name in INGREDIENTS_BY_CATEGORY.keys():
                Category.objects.get_or_create(name=category_name)
            categories = list(Category.objects.all())

        # Create recipes
        recipes_created = 0
        for i in range(count):
            # Select a random title or generate one
            if i < len(RECIPE_TITLES):
                title = RECIPE_TITLES[i]
            else:
                title = f"{random.choice(ADJECTIVES).capitalize()} {random.choice(list(INGREDIENTS_BY_CATEGORY.keys()))} {random.choice(['Dish', 'Meal', 'Recipe', 'Delight', 'Special'])}"

            # Select random categories (1-3)
            recipe_categories = random.sample(categories, random.randint(1, 3))

            # Generate description
            category_name = recipe_categories[0].name
            description = random.choice(DESCRIPTIONS).format(
                category=category_name,
                adjective=random.choice(ADJECTIVES),
                meal=random.choice(MEALS),
                time=random.randint(15, 60),
            )

            # Generate instructions
            template = random.choice(INSTRUCTIONS_TEMPLATES)
            steps = random.sample(COOKING_STEPS, 3)
            instructions = template.format(
                step1=steps[0],
                step2=steps[1],
                step3=steps[2],
                temp=random.choice([350, 375, 400, 425]),
                time=random.randint(10, 45),
            )

            # Create recipe
            recipe = Recipe.objects.create(
                title=title,
                description=description,
                instructions=instructions,
                author=user,
                cooking_time=random.randint(15, 120),
                difficulty=random.choice(["easy", "medium", "hard"]),
                created_at=timezone.now()
                - timezone.timedelta(days=random.randint(0, 365)),
            )

            # Add categories
            recipe.categories.set(recipe_categories)

            # Add ingredients (5-10)
            ingredient_pool = []
            for category in recipe_categories:
                if category.name in INGREDIENTS_BY_CATEGORY:
                    ingredient_pool.extend(INGREDIENTS_BY_CATEGORY[category.name])

            # If no specific ingredients for the category, use a general list
            if not ingredient_pool:
                ingredient_pool = [
                    "salt",
                    "pepper",
                    "olive oil",
                    "garlic",
                    "onion",
                    "flour",
                    "sugar",
                    "butter",
                    "eggs",
                    "milk",
                    "chicken",
                    "beef",
                    "pasta",
                    "rice",
                    "potatoes",
                    "tomatoes",
                    "cheese",
                    "lemon",
                    "herbs",
                    "spices",
                ]

            # Ensure unique ingredients
            if len(ingredient_pool) > 10:
                ingredients_to_add = random.sample(
                    ingredient_pool, random.randint(5, 10)
                )
            else:
                ingredients_to_add = ingredient_pool

            for ingredient_name in ingredients_to_add:
                Ingredient.objects.create(name=ingredient_name, recipe=recipe)

            # Add ratings (0-5)
            num_ratings = random.randint(0, 5)
            for _ in range(num_ratings):
                # Get a random user or use the author
                if User.objects.count() > 1 and random.random() > 0.5:
                    rating_user = User.objects.exclude(id=user.id).order_by("?").first()
                else:
                    rating_user = user

                # Check if rating already exists
                if not Rating.objects.filter(recipe=recipe, user=rating_user).exists():
                    # Create rating
                    Rating.objects.create(
                        recipe=recipe,
                        user=rating_user,
                        score=random.randint(3, 5),  # Bias towards positive ratings
                    )

            # Add comments (0-3)
            num_comments = random.randint(0, 3)
            for _ in range(num_comments):
                # Get a random user or use the author
                if User.objects.count() > 1 and random.random() > 0.5:
                    comment_user = (
                        User.objects.exclude(id=user.id).order_by("?").first()
                    )
                else:
                    comment_user = user

                # Create comment
                Comment.objects.create(
                    recipe=recipe,
                    user=comment_user,
                    content=fake.paragraph(),
                    created_at=recipe.created_at
                    + timezone.timedelta(days=random.randint(1, 30)),
                )

            recipes_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {recipes_created} recipes")
        )
