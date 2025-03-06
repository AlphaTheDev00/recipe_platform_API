import json
from django.core.management.base import BaseCommand
from api.models import Recipe, Category

class Command(BaseCommand):
    help = 'Fix categories stored as strings in the database'

    def handle(self, *args, **options):
        # Get all recipes
        recipes = Recipe.objects.all()
        self.stdout.write(f"Found {len(recipes)} recipes to check")
        
        fixed_count = 0
        
        for recipe in recipes:
            # Get all categories for this recipe
            categories = list(recipe.categories.all())
            category_names = [c.name for c in categories]
            
            self.stdout.write(f"Recipe {recipe.id}: {recipe.title}")
            self.stdout.write(f"  Current categories: {category_names}")
            
            # Check if we need to fix any string representation
            # This is a bit tricky as we don't know exactly how the data is stored
            # Let's try a few approaches
            
            # 1. Check if any category name looks like a JSON string
            for category in categories:
                if category.name.startswith('[') and category.name.endswith(']'):
                    try:
                        # Try to parse as JSON
                        parsed_names = json.loads(category.name)
                        if isinstance(parsed_names, list):
                            self.stdout.write(f"  Found JSON string category: {category.name}")
                            
                            # Remove this category
                            recipe.categories.remove(category)
                            
                            # Add individual categories
                            for name in parsed_names:
                                clean_name = name.strip().replace('"', '')
                                new_category, created = Category.objects.get_or_create(
                                    name=clean_name,
                                    defaults={"description": ""}
                                )
                                recipe.categories.add(new_category)
                                if created:
                                    self.stdout.write(f"  Created new category: {clean_name}")
                            
                            fixed_count += 1
                            self.stdout.write(f"  Fixed categories for recipe {recipe.id}")
                    except json.JSONDecodeError:
                        self.stdout.write(f"  Error parsing category: {category.name}")
        
        self.stdout.write(self.style.SUCCESS(f"Fixed categories for {fixed_count} recipes"))
