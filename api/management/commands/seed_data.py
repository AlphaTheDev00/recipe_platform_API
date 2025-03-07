import random
import sys
import argparse
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import (
    Recipe,
    Ingredient,
    Category,
    Rating,
    Comment,
    Favorite,
    UserProfile,
)
from faker import Faker
from django.utils import timezone
from datetime import timedelta

fake = Faker()

# Sample food recipes - expanded collection
SAMPLE_RECIPES = [
    {
        "title": "Spaghetti Carbonara",
        "description": "A classic Italian pasta dish with a creamy sauce made with eggs, cheese, and pancetta.",
        "instructions": "1. Cook spaghetti according to package instructions.\n2. In a separate pan, cook pancetta until crispy.\n3. Beat eggs and mix with grated cheese.\n4. Drain pasta and immediately toss with egg mixture and pancetta.\n5. Season with black pepper and serve immediately.",
        "cooking_time": 20,
        "difficulty": "medium",
        "ingredients": [
            "spaghetti",
            "eggs",
            "pancetta",
            "Pecorino Romano cheese",
            "black pepper",
            "salt",
        ],
        "categories": ["Italian", "Dinner", "Quick Meals"],
    },
    {
        "title": "Chocolate Chip Cookies",
        "description": "Soft, chewy cookies loaded with chocolate chips. A classic favorite!",
        "instructions": "1. Preheat oven to 350°F (175°C).\n2. Cream butter and sugars until light and fluffy.\n3. Beat in eggs and vanilla.\n4. Mix in flour, baking soda, and salt.\n5. Fold in chocolate chips.\n6. Drop by rounded tablespoons onto cookie sheets.\n7. Bake for 10-12 minutes until edges are golden brown.",
        "cooking_time": 30,
        "difficulty": "easy",
        "ingredients": [
            "butter",
            "white sugar",
            "brown sugar",
            "eggs",
            "vanilla extract",
            "flour",
            "baking soda",
            "salt",
            "chocolate chips",
        ],
        "categories": ["Desserts", "Baking", "American"],
    },
    {
        "title": "Greek Salad",
        "description": "Fresh and colorful salad with tomatoes, cucumbers, olives, and feta cheese.",
        "instructions": "1. Chop tomatoes, cucumber, and bell pepper.\n2. Slice the red onion thinly.\n3. Combine vegetables in a bowl.\n4. Add olives and crumbled feta cheese.\n5. Dress with olive oil, lemon juice, oregano, salt, and pepper.\n6. Toss gently to combine.",
        "cooking_time": 15,
        "difficulty": "easy",
        "ingredients": [
            "tomatoes",
            "cucumber",
            "red onion",
            "bell pepper",
            "Kalamata olives",
            "feta cheese",
            "olive oil",
            "lemon juice",
            "oregano",
            "salt",
            "pepper",
        ],
        "categories": ["Greek", "Salads", "Vegetarian", "Healthy"],
    },
    {
        "title": "Homemade Pizza",
        "description": "Delicious pizza with a crispy crust and your favorite toppings.",
        "instructions": "1. Prepare the pizza dough and let it rise.\n2. Roll out the dough into a circle.\n3. Spread sauce over the dough, leaving a border for the crust.\n4. Add cheese and toppings of your choice.\n5. Bake in a preheated oven at 475°F for 10-12 minutes until golden.",
        "cooking_time": 40,
        "difficulty": "medium",
        "ingredients": [
            "pizza dough",
            "tomato sauce",
            "mozzarella cheese",
            "olive oil",
            "basil",
            "garlic",
            "pepperoni",
            "bell peppers",
            "mushrooms",
            "onions",
        ],
        "categories": ["Italian", "Dinner", "Comfort Food", "Baking"],
    },
    {
        "title": "Beef Stir Fry",
        "description": "Quick and flavorful beef stir fry with vegetables and a savory sauce.",
        "instructions": "1. Slice beef thinly against the grain.\n2. Chop vegetables into bite-sized pieces.\n3. Heat oil in wok over high heat.\n4. Stir-fry beef until browned.\n5. Remove beef and stir-fry vegetables.\n6. Add sauce ingredients and bring to simmer.\n7. Return beef to wok and toss to combine.",
        "cooking_time": 25,
        "difficulty": "medium",
        "ingredients": [
            "beef sirloin",
            "broccoli",
            "carrots",
            "bell peppers",
            "onion",
            "garlic",
            "ginger",
            "soy sauce",
            "oyster sauce",
            "cornstarch",
            "vegetable oil",
        ],
        "categories": ["Asian", "Chinese", "Dinner", "High Protein"],
    },
    {
        "title": "Guacamole",
        "description": "Fresh homemade guacamole with avocados, lime, and cilantro.",
        "instructions": "1. Cut avocados in half and remove pits.\n2. Scoop out avocado flesh into a bowl.\n3. Mash avocados with a fork.\n4. Stir in diced onion, tomato, cilantro, lime juice, and jalapeño.\n5. Season with salt and pepper.\n6. Serve immediately with tortilla chips.",
        "cooking_time": 10,
        "difficulty": "easy",
        "ingredients": [
            "avocados",
            "lime",
            "cilantro",
            "onion",
            "tomato",
            "jalapeño",
            "salt",
            "pepper",
        ],
        "categories": ["Mexican", "Appetizers", "Vegetarian", "Dips"],
    },
    {
        "title": "Chicken Tikka Masala",
        "description": "Tender chicken in a rich and creamy tomato sauce with Indian spices.",
        "instructions": "1. Marinate chicken in yogurt and spices for at least 1 hour.\n2. Grill or broil chicken until slightly charred.\n3. In a separate pan, sauté onions, garlic, and ginger.\n4. Add spices and tomato sauce, simmer for 10 minutes.\n5. Add cream and grilled chicken.\n6. Simmer for 15 minutes and garnish with cilantro.",
        "cooking_time": 60,
        "difficulty": "medium",
        "ingredients": [
            "chicken breast",
            "yogurt",
            "garam masala",
            "turmeric",
            "cumin",
            "coriander",
            "onion",
            "garlic",
            "ginger",
            "tomato sauce",
            "heavy cream",
            "cilantro",
        ],
        "categories": ["Indian", "Dinner", "Chicken"],
    },
    {
        "title": "Berry Smoothie Bowl",
        "description": "Refreshing smoothie bowl topped with fresh fruits, granola, and nuts.",
        "instructions": "1. Blend frozen berries, banana, yogurt, and milk until smooth.\n2. Pour into a bowl.\n3. Top with fresh berries, sliced banana, granola, and nuts.\n4. Drizzle with honey if desired.",
        "cooking_time": 10,
        "difficulty": "easy",
        "ingredients": [
            "frozen mixed berries",
            "banana",
            "yogurt",
            "milk",
            "fresh berries",
            "granola",
            "almonds",
            "honey",
        ],
        "categories": ["Breakfast", "Healthy", "Vegetarian", "Quick Meals"],
    },
    {
        "title": "Vegetable Lasagna",
        "description": "Hearty vegetable lasagna layered with ricotta cheese and marinara sauce.",
        "instructions": "1. Preheat oven to 375°F (190°C).\n2. Sauté vegetables until tender.\n3. Mix ricotta with eggs and herbs.\n4. Layer sauce, lasagna noodles, vegetables, ricotta mixture, and mozzarella in baking dish.\n5. Repeat layers ending with sauce and mozzarella on top.\n6. Cover with foil and bake for 25 minutes.\n7. Remove foil and bake for additional 25 minutes.",
        "cooking_time": 90,
        "difficulty": "hard",
        "ingredients": [
            "lasagna noodles",
            "zucchini",
            "spinach",
            "mushrooms",
            "onion",
            "garlic",
            "ricotta cheese",
            "eggs",
            "mozzarella cheese",
            "parmesan cheese",
            "marinara sauce",
            "Italian herbs",
        ],
        "categories": ["Italian", "Vegetarian", "Dinner", "Baking"],
    },
    {
        "title": "Fish Tacos",
        "description": "Crispy fish tacos with cabbage slaw and tangy sauce.",
        "instructions": "1. Season fish fillets with spices.\n2. Cook fish until flaky.\n3. Mix cabbage, lime juice, and mayonnaise for slaw.\n4. Warm tortillas.\n5. Assemble tacos with fish, slaw, and avocado.\n6. Serve with lime wedges.",
        "cooking_time": 25,
        "difficulty": "medium",
        "ingredients": [
            "white fish fillets",
            "cumin",
            "paprika",
            "cabbage",
            "lime",
            "mayonnaise",
            "corn tortillas",
            "avocado",
            "cilantro",
        ],
        "categories": ["Mexican", "Seafood", "Lunch", "Quick Meals"],
    },
    {
        "title": "Apple Pie",
        "description": "Classic homemade apple pie with a flaky crust and cinnamon-spiced filling.",
        "instructions": "1. Prepare pie crust and line pie dish.\n2. Mix sliced apples with sugar, cinnamon, nutmeg, and lemon juice.\n3. Fill pie crust with apple mixture and dot with butter.\n4. Add top crust and seal edges.\n5. Cut vents in top crust.\n6. Bake at 425°F for 15 minutes, then reduce to 350°F for 35-45 minutes.",
        "cooking_time": 90,
        "difficulty": "hard",
        "ingredients": [
            "pie crust",
            "apples",
            "sugar",
            "cinnamon",
            "nutmeg",
            "lemon juice",
            "butter",
            "egg (for wash)",
        ],
        "categories": ["Desserts", "American", "Baking", "Fruit"],
    },
    {
        "title": "Mashed Potatoes",
        "description": "Creamy, buttery mashed potatoes - the perfect comfort food side dish.",
        "instructions": "1. Peel and cube potatoes.\n2. Boil in salted water until tender.\n3. Drain well and return to pot.\n4. Add butter, milk, and sour cream.\n5. Mash until smooth and creamy.\n6. Season with salt and pepper to taste.",
        "cooking_time": 30,
        "difficulty": "easy",
        "ingredients": [
            "russet potatoes",
            "butter",
            "milk",
            "sour cream",
            "salt",
            "pepper",
            "garlic powder",
        ],
        "categories": ["Side Dish", "American", "Comfort Food", "Vegetarian"],
    },
    {
        "title": "French Onion Soup",
        "description": "Rich beef broth with caramelized onions, topped with bread and melted cheese.",
        "instructions": "1. Slice onions thinly.\n2. Cook onions in butter over low heat for 45 minutes until deeply caramelized.\n3. Add beef broth and herbs, simmer for 30 minutes.\n4. Ladle into oven-safe bowls.\n5. Top with toasted bread and grated Gruyère cheese.\n6. Broil until cheese is melted and golden.",
        "cooking_time": 90,
        "difficulty": "medium",
        "ingredients": [
            "onions",
            "butter",
            "beef broth",
            "bay leaf",
            "thyme",
            "baguette",
            "Gruyère cheese",
            "salt",
            "pepper",
        ],
        "categories": ["French", "Soup", "Comfort Food", "Dinner"],
    },
    {
        "title": "Banana Bread",
        "description": "Moist and flavorful banana bread with a tender crumb. Perfect for using overripe bananas.",
        "instructions": "1. Preheat oven to 350°F (175°C).\n2. Mash bananas in a large bowl.\n3. Add melted butter, sugar, egg, and vanilla.\n4. Mix in flour, baking soda, and salt.\n5. Pour into greased loaf pan.\n6. Bake for 55-60 minutes until a toothpick inserted comes out clean.",
        "cooking_time": 65,
        "difficulty": "easy",
        "ingredients": [
            "ripe bananas",
            "butter",
            "sugar",
            "egg",
            "vanilla extract",
            "flour",
            "baking soda",
            "salt",
            "cinnamon",
            "walnuts (optional)",
        ],
        "categories": ["Breakfast", "Baking", "Desserts", "Fruit"],
    },
    {
        "title": "Pad Thai",
        "description": "Classic Thai stir-fried noodles with a perfect balance of sweet, sour, and savory flavors.",
        "instructions": "1. Soak rice noodles in hot water until softened.\n2. Stir-fry shrimp or chicken in oil.\n3. Add beaten eggs and cook until set.\n4. Add noodles, bean sprouts, and sauce.\n5. Toss until well combined and heated through.\n6. Garnish with peanuts, green onions, and lime wedges.",
        "cooking_time": 30,
        "difficulty": "medium",
        "ingredients": [
            "rice noodles",
            "shrimp or chicken",
            "eggs",
            "bean sprouts",
            "garlic",
            "fish sauce",
            "tamarind paste",
            "palm sugar",
            "lime",
            "peanuts",
            "green onions",
        ],
        "categories": ["Thai", "Asian", "Dinner", "Noodles"],
    },
    {
        "title": "Roast Chicken",
        "description": "Simple and classic roasted whole chicken with herbs and lemon.",
        "instructions": "1. Preheat oven to 425°F (220°C).\n2. Pat chicken dry and season cavity with salt and pepper.\n3. Stuff with lemon and herbs.\n4. Rub skin with butter and season.\n5. Roast for 1 hour 15 minutes, or until internal temperature reaches 165°F.\n6. Rest for 15 minutes before carving.",
        "cooking_time": 90,
        "difficulty": "medium",
        "ingredients": [
            "whole chicken",
            "lemon",
            "rosemary",
            "thyme",
            "garlic",
            "butter",
            "salt",
            "pepper",
            "olive oil",
        ],
        "categories": ["Dinner", "Chicken", "Comfort Food", "American"],
    },
]

# Food-focused categories
CATEGORIES = [
    "Breakfast",
    "Lunch",
    "Dinner",
    "Desserts",
    "Snacks",
    "Italian",
    "Mexican",
    "Asian",
    "Thai",
    "Indian",
    "American",
    "Greek",
    "French",
    "Vegetarian",
    "Vegan",
    "Gluten-Free",
    "Dairy-Free",
    "Quick Meals",
    "Side Dish",
    "Slow Cooker",
    "Baking",
    "Grilling",
    "Healthy",
    "Comfort Food",
    "Budget Friendly",
    "Gourmet",
    "Seafood",
    "Chicken",
    "Beef",
    "Pork",
    "Appetizers",
    "Soups",
    "Salads",
    "Pasta",
    "Noodles",
    "Rice",
    "High Protein",
    "Low Carb",
    "Fruit",
    "Vegetables",
    "Dips",
]

FOOD_ADJECTIVES = [
    "Savory",
    "Sweet",
    "Spicy",
    "Tangy",
    "Creamy",
    "Crispy",
    "Juicy",
    "Fresh",
    "Homemade",
    "Roasted",
    "Grilled",
    "Baked",
    "Fried",
    "Steamed",
    "Slow-cooked",
    "Sautéed",
    "Glazed",
    "Hearty",
    "Light",
    "Rich",
    "Zesty",
    "Fragrant",
    "Smoky",
    "Herbed",
    "Buttery",
]

FOOD_TYPES = [
    "Pasta",
    "Rice",
    "Soup",
    "Salad",
    "Stew",
    "Curry",
    "Stir-fry",
    "Casserole",
    "Sandwich",
    "Burger",
    "Pizza",
    "Tacos",
    "Risotto",
    "Roast",
    "Pie",
    "Cake",
    "Cookies",
    "Bread",
    "Muffins",
    "Chicken",
    "Beef",
    "Pork",
    "Fish",
    "Seafood",
    "Tofu",
    "Vegetables",
    "Noodles",
    "Pancakes",
    "Waffles",
    "Omelette",
    "Frittata",
    "Paella",
    "Lasagna",
]

FOOD_INGREDIENTS = [
    "chicken",
    "beef",
    "pork",
    "fish",
    "shrimp",
    "tofu",
    "eggs",
    "cheese",
    "pasta",
    "rice",
    "potatoes",
    "tomatoes",
    "onions",
    "garlic",
    "bell peppers",
    "broccoli",
    "spinach",
    "mushrooms",
    "carrots",
    "flour",
    "sugar",
    "butter",
    "milk",
    "cream",
    "olive oil",
    "lemon",
    "lime",
    "herbs",
    "spices",
    "salt",
    "pepper",
    "bread",
    "beans",
    "chickpeas",
    "quinoa",
    "corn",
    "peas",
    "avocado",
    "cucumbers",
]


class Command(BaseCommand):
    help = "Seed database with food recipe data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=5, help="Number of users to create"
        )
        parser.add_argument(
            "--recipes",
            type=int,
            default=10,
            help="Number of additional random recipes to create",
        )
        parser.add_argument(
            "--ratings", type=int, default=50, help="Number of ratings to create"
        )
        parser.add_argument(
            "--comments", type=int, default=30, help="Number of comments to create"
        )
        parser.add_argument(
            "--favorites", type=int, default=20, help="Number of favorites to create"
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        # Always clear existing data
        self.stdout.write("Clearing existing data...")
        Favorite.objects.all().delete()
        Rating.objects.all().delete()
        Comment.objects.all().delete()
        Ingredient.objects.all().delete()
        Recipe.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS("Database cleared successfully!"))
        
        # Force 50 recipes
        options['recipes'] = 50

        if should_clear:
            self.stdout.write("Clearing existing data...")
            Favorite.objects.all().delete()
            Rating.objects.all().delete()
            Comment.objects.all().delete()
            Ingredient.objects.all().delete()
            Recipe.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Database cleared successfully!"))

        # Create superuser if it doesn't exist
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Created superuser: admin/admin123"))

        # Create normal users
        users = []
        for i in range(options["users"]):
            username = f"user{i+1}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                )
                users.append(user)
                self.stdout.write(f"Created user: {username}")

        # If no users were created (because they already existed), get existing ones
        if not users:
            users = User.objects.filter(is_superuser=False)[: options["users"]]

        # Create categories
        categories = {}
        for category_name in CATEGORIES:
            category, created = Category.objects.get_or_create(name=category_name)
            categories[category_name] = category
            if created:
                self.stdout.write(f"Created category: {category_name}")

        # Create sample recipes
        sample_recipes_created = 0
        for recipe_data in SAMPLE_RECIPES:
            if Recipe.objects.filter(title=recipe_data["title"]).exists():
                continue

            # Create recipe with only the fields that exist in the model
            author = random.choice(users)
            recipe = Recipe.objects.create(
                title=recipe_data["title"],
                description=recipe_data["description"],
                instructions=recipe_data["instructions"],
                cooking_time=recipe_data["cooking_time"],
                difficulty=recipe_data["difficulty"],
                author=author,
            )

            # Add ingredients
            for ingredient_name in recipe_data["ingredients"]:
                Ingredient.objects.create(recipe=recipe, name=ingredient_name)

            # Add categories
            for category_name in recipe_data["categories"]:
                if category_name in categories:
                    recipe.categories.add(categories[category_name])

            sample_recipes_created += 1
            self.stdout.write(f"Created sample recipe: {recipe.title}")

        # Create additional random recipes if specified
        random_recipes_created = 0
        for i in range(options["recipes"]):
            # Generate food-related title instead of random sentence
            adjective = random.choice(FOOD_ADJECTIVES)
            food_type = random.choice(FOOD_TYPES)
            title = f"{adjective} {food_type}"

            # Skip if recipe with this title already exists
            if Recipe.objects.filter(title=title).exists():
                continue

            # Create recipe
            author = random.choice(users)

            cooking_time = random.randint(10, 120)
            difficulty_choices = ["easy", "medium", "hard"]

            # Create food-focused description
            description = f"A delicious {adjective.lower()} {food_type.lower()} recipe that's perfect for any occasion."

            # Create realistic instructions
            instructions = "1. Gather all ingredients and prepare your workspace.\n"
            instructions += "2. Chop and measure ingredients as needed.\n"
            steps = random.randint(3, 8)
            for step in range(3, steps + 3):
                if step == 3:
                    instructions += f"{step}. Combine main ingredients in a bowl.\n"
                elif step == steps + 2:
                    instructions += f"{step}. Serve and enjoy!\n"
                else:
                    instructions += f"{step}. {random.choice(['Cook', 'Mix', 'Stir', 'Add', 'Fold in', 'Simmer', 'Bake', 'Prepare'])} for {random.randint(5, 30)} minutes.\n"

            recipe = Recipe.objects.create(
                title=title,
                description=description,
                instructions=instructions,
                cooking_time=cooking_time,
                difficulty=random.choice(difficulty_choices),
                author=author,
            )

            # Add ingredients (3-10 random ingredients)
            ingredient_count = random.randint(3, 10)
            used_ingredients = random.sample(
                FOOD_INGREDIENTS, min(ingredient_count, len(FOOD_INGREDIENTS))
            )
            for ingredient in used_ingredients:
                Ingredient.objects.create(recipe=recipe, name=ingredient)

            # Add 1-4 categories
            category_count = random.randint(1, 4)
            random_categories = random.sample(list(categories.values()), category_count)
            for category in random_categories:
                recipe.categories.add(category)

            random_recipes_created += 1
            self.stdout.write(f"Created random recipe: {recipe.title}")

        # All recipes
        recipes = Recipe.objects.all()

        # Create ratings
        ratings_created = 0
        for _ in range(options["ratings"]):
            user = random.choice(users)
            recipe = random.choice(recipes)

            # Skip if rating already exists
            if Rating.objects.filter(user=user, recipe=recipe).exists():
                continue

            score = random.randint(1, 5)

            # Add some variance to created dates
            days_ago = random.randint(0, 60)
            created_at = timezone.now() - timedelta(days=days_ago)

            Rating.objects.create(
                user=user, recipe=recipe, score=score, created_at=created_at
            )
            ratings_created += 1

        # Create comments
        comments_created = 0
        for _ in range(options["comments"]):
            user = random.choice(users)
            recipe = random.choice(recipes)

            # Add some variance to created dates
            days_ago = random.randint(0, 60)
            created_at = timezone.now() - timedelta(days_ago)

            Comment.objects.create(
                user=user,
                recipe=recipe,
                content=fake.paragraph(),
                created_at=created_at,
            )
            comments_created += 1

        # Create favorites
        favorites_created = 0
        for _ in range(options["favorites"]):
            user = random.choice(users)
            recipe = random.choice(recipes)

            # Skip if favorite already exists
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                continue

            # Add some variance to created dates
            days_ago = random.randint(0, 60)
            created_at = timezone.now() - timedelta(days_ago)

            Favorite.objects.create(user=user, recipe=recipe, created_at=created_at)
            favorites_created += 1

        # Summary
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded database:"))
        self.stdout.write(f"- Users: {len(users)} users")
        self.stdout.write(f"- Categories: {len(CATEGORIES)}")
        self.stdout.write(f"- Sample recipes: {sample_recipes_created}")
        self.stdout.write(f"- Random recipes: {random_recipes_created}")
        self.stdout.write(f"- Total recipes: {Recipe.objects.count()}")
        self.stdout.write(f"- Ratings: {ratings_created}")
        self.stdout.write(f"- Comments: {comments_created}")
        self.stdout.write(f"- Favorites: {favorites_created}")
        self.stdout.write(self.style.SUCCESS("Done!"))
