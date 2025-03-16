from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create demo users
for i in range(1, 6):
    username = f"user{i}"
    email = f"user{i}@example.com"
    password = "password123"
    
    # Check if user already exists
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, email=email, password=password)
        # Create token for the user
        Token.objects.get_or_create(user=user)
        print(f"Created user: {username}")
    else:
        print(f"User {username} already exists")
