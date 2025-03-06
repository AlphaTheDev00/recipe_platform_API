from django.db import migrations

def create_initial_categories(apps, schema_editor):
    Category = apps.get_model('api', 'Category')
    initial_categories = [
        {'name': 'Breakfast', 'description': 'Morning meals and breakfast dishes'},
        {'name': 'Lunch', 'description': 'Midday meals and lunch recipes'},
        {'name': 'Dinner', 'description': 'Evening meals and dinner recipes'},
        {'name': 'Dessert', 'description': 'Sweet treats and desserts'},
        {'name': 'Appetizer', 'description': 'Starters and appetizers'},
        {'name': 'Snack', 'description': 'Light bites and snacks'},
        {'name': 'Soup', 'description': 'Soups and broths'},
        {'name': 'Salad', 'description': 'Fresh salads and dressings'},
        {'name': 'Beverage', 'description': 'Drinks and beverages'},
        {'name': 'Baking', 'description': 'Baked goods and pastries'},
    ]
    
    for category_data in initial_categories:
        Category.objects.create(**category_data)

def remove_initial_categories(apps, schema_editor):
    Category = apps.get_model('api', 'Category')
    Category.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0003_category_recipe_cooking_time_recipe_difficulty_and_more'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories, remove_initial_categories),
    ]