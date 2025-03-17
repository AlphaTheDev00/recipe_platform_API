# Savora Recipe Platform

## Description
Savora is a full-stack recipe sharing platform developed as part of my software engineering bootcamp at General Assembly. This project demonstrates my ability to create a complete web application with a Django REST Framework backend API and a React frontend. Users can discover, create, share, and manage their favorite recipes in a seamless and intuitive interface.

## Deployment Link
- **Frontend**: [https://savora-recipe.netlify.app](https://savora-recipe.netlify.app)
- **API**: [https://savora-recipe-b7493c60c573-2ac1db511588.herokuapp.com/](https://savora-recipe-b7493c60c573-2ac1db511588.herokuapp.com/)

### Demo Accounts
For testing purposes, the following accounts are available:

**Regular Users:**
- Usernames: user1, user2, user3, user4, user5
- Password for all accounts: password123

**Admin Account:**
- Username: admin
- Password: admin123

## Getting Started/Code Installation

### Backend Setup
1. Clone the repository
   ```bash
   git clone <repository-url>
   cd recipe_api
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (copy from .env.example)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations
   ```bash
   python manage.py migrate
   ```

6. Seed the database with sample data (optional)
   ```bash
   python manage.py seed_recipes
   ```

7. Run the development server
   ```bash
   python manage.py runserver
   ```

### Frontend Setup
1. Navigate to the frontend directory
   ```bash
   cd ../recipe-frontend
   ```

2. Install dependencies
   ```bash
   npm install
   ```

3. Set up environment variables (copy from .env.example)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the development server
   ```bash
   npm run dev
   ```

5. Open your browser and navigate to http://localhost:5173

## Timeframe & Working Team
This project was completed as a solo project over a two-week sprint. I was responsible for all aspects of the application, from planning and design to implementation and deployment.

## Technologies Used

### Frontend
- **React 19**: Component-based UI library
- **React Router 7**: For client-side routing
- **Axios**: HTTP client for API requests
- **Bootstrap 5**: CSS framework for responsive design
- **Vite**: Build tool and development server
- **Netlify**: Frontend deployment platform

### Backend
- **Django 5.1**: Python web framework
- **Django REST Framework**: API development toolkit
- **PostgreSQL**: Relational database
- **Token Authentication**: For secure user authentication
- **Cloudinary**: Cloud storage for media files
- **Heroku**: Backend deployment platform

### Development Tools
- **Git & GitHub**: Version control
- **VS Code**: Code editor
- **Postman**: API testing
- **Figma**: UI/UX design
- **Trello**: Project management

## Brief
The project brief required the development of a full-stack application with the following specifications:

- Create a RESTful API using Django REST Framework
- Implement a React frontend that consumes the API
- Include user authentication and authorization
- Implement CRUD functionality for at least one resource
- Design a responsive and intuitive user interface
- Deploy both frontend and backend to production environments
- Include comprehensive documentation

## Planning

### Entity Relationship Diagram (ERD)
I began by designing the database schema to model the relationships between users, recipes, ingredients, categories, ratings, comments, and favorites.

![Entity Relationship Diagram](https://example.com/erd.png)

### Wireframes
I created wireframes for all key pages to plan the user interface and experience before starting development.

![Wireframe - Home Page](https://example.com/wireframe-home.png)
![Wireframe - Recipe Detail](https://example.com/wireframe-detail.png)

### User Stories
I developed user stories to guide the feature development:

- As a user, I want to browse recipes without logging in
- As a user, I want to create an account to save my favorite recipes
- As a user, I want to create, edit, and delete my own recipes
- As a user, I want to rate and comment on recipes
- As a user, I want to filter recipes by category or difficulty
- As a user, I want to customize my profile with my cooking preferences

### Project Management
I used Trello to manage the project tasks, organizing them into sprints and tracking progress.

![Trello Board](https://example.com/trello.png)

## Build/Code Process

### Backend Development
I started by setting up the Django project and creating the models for the recipe application. The Recipe model is the core of the application, with relationships to other models like User, Category, and Ingredient.

```python
class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name="recipes", blank=True)
    cooking_time = models.PositiveIntegerField(
        help_text="Cooking time in minutes", null=True, blank=True
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        default="medium",
    )
    image = models.ImageField(upload_to="recipe_images/", null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title
```

Next, I implemented the serializers to convert model instances to JSON for the API. I created nested serializers to include related data in the responses, such as ingredients and category details in the recipe response.

```python
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, required=False)
    author = UserSerializer(read_only=True)
    category_details = CategorySerializer(source='categories', many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = '__all__'
        
    def get_avg_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            return sum(rating.score for rating in ratings) / len(ratings)
        return None
        
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
            
        return recipe
```

I implemented token-based authentication to secure the API, allowing read access without authentication but requiring authentication for write operations.

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}
```

### Frontend Development
For the frontend, I set up a React application using Vite and implemented the component structure. I created a context for authentication to manage user state across the application.

```jsx
// AuthContext.jsx
import { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl } from '../utils/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(getApiUrl('api/users/profile/'), {
        headers: { Authorization: `Token ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(getApiUrl('api-token-auth/'), {
        username,
        password
      });
      const newToken = response.data.token;
      localStorage.setItem('token', newToken);
      setToken(newToken);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
```

I implemented the RecipeDetail component to display comprehensive information about a recipe, including ingredients, instructions, ratings, and comments.

```jsx
// RecipeDetail.jsx (partial)
const RecipeDetail = () => {
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const { id } = useParams();
  const { user } = useAuth();

  useEffect(() => {
    const fetchRecipe = async () => {
      try {
        const data = await forceRefresh(`api/recipes/${id}/`);
        setRecipe(data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching recipe:", err);
        setLoading(false);
      }
    };

    fetchRecipe();
  }, [id]);

  return (
    <div className="container d-flex justify-content-center">
      {loading ? (
        <div className="text-center loading">Loading...</div>
      ) : (
        <div className="recipe-detail">
          <div className="card">
            <img
              src={recipe.image_url || getImageUrl(recipe.image, recipe.id)}
              className="card-img-top"
              alt={recipe.title}
            />
            <div className="card-body">
              <h2 className="card-title">{recipe.title}</h2>
              <p className="card-text">{recipe.description}</p>
              
              {/* Ingredients section */}
              <div className="mb-4">
                <h4>Ingredients:</h4>
                <ul className="list-group">
                  {recipe.ingredients.map((ingredient, index) => (
                    <li key={index} className="list-group-item">
                      {ingredient.name}
                    </li>
                  ))}
                </ul>
              </div>
              
              {/* Instructions section */}
              <div className="mb-4">
                <h4>Instructions:</h4>
                <ol className="instructions-list">
                  {recipe.instructions
                    .split("\n")
                    .filter((step) => step.trim())
                    .map((step, index) => (
                      <li key={index} className="instruction-step">
                        {step.replace(/^\d+\.\s*/, "")}
                      </li>
                    ))}
                </ol>
              </div>
              
              {/* Rating and comments component */}
              <RatingAndComments recipeId={id} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

## Challenges

### API Data Fetching
One of the main challenges I faced was handling the complex nested data structure in the API responses. The recipe data included nested objects for ingredients, categories, and user information. I had to carefully design the serializers to ensure all the necessary data was included in the responses without causing performance issues.

To solve this, I implemented custom serializer methods and used SerializerMethodFields to include calculated data like average ratings:

```python
def get_avg_rating(self, obj):
    ratings = obj.ratings.all()
    if ratings:
        return sum(rating.score for rating in ratings) / len(ratings)
    return None
```

### Image Handling
Another challenge was implementing image uploads and storage. I initially stored images locally, but this wasn't suitable for production. I integrated Cloudinary for cloud storage, which required configuring the Django settings and updating the frontend to handle image URLs correctly.

```python
# settings.py
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# Use Cloudinary for media storage in production
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### Authentication Flow
Implementing a secure authentication flow was challenging. I needed to ensure that the token was properly stored and included in API requests, while also handling token expiration and user logout.

I created utility functions to handle API requests with authentication:

```javascript
// api.js
export const getApiUrl = (endpoint) => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/';
  return `${baseUrl}${endpoint}`;
};

export const safeFetch = async (endpoint, options = {}) => {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Token ${token}` } : {}),
    ...options.headers,
  };

  try {
    const response = await axios({
      url: getApiUrl(endpoint),
      ...options,
      headers,
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    throw error;
  }
};
```

## Wins

### Responsive Design
I'm particularly proud of the responsive design implementation. The application looks great and functions well on all device sizes, from mobile phones to desktop computers. I used Bootstrap's grid system and custom CSS to ensure a consistent user experience across devices.

### Complex Form Handling
Implementing the recipe creation and editing forms was a significant achievement. These forms needed to handle multiple ingredients, categories, and image uploads, all while providing a smooth user experience.

```jsx
// RecipeForm.jsx (partial)
const RecipeForm = ({ initialData, onSubmit }) => {
  const [formData, setFormData] = useState(initialData || {
    title: '',
    description: '',
    instructions: '',
    cooking_time: '',
    difficulty: 'medium',
    categories: [],
    ingredients: [{ name: '' }]
  });

  const handleIngredientChange = (index, value) => {
    const updatedIngredients = [...formData.ingredients];
    updatedIngredients[index] = { name: value };
    setFormData({ ...formData, ingredients: updatedIngredients });
  };

  const addIngredient = () => {
    setFormData({
      ...formData,
      ingredients: [...formData.ingredients, { name: '' }]
    });
  };

  const removeIngredient = (index) => {
    const updatedIngredients = formData.ingredients.filter((_, i) => i !== index);
    setFormData({ ...formData, ingredients: updatedIngredients });
  };

  // Form submission and other handlers...

  return (
    <form onSubmit={handleSubmit}>
      {/* Other form fields... */}
      
      <div className="mb-3">
        <label className="form-label">Ingredients</label>
        {formData.ingredients.map((ingredient, index) => (
          <div key={index} className="input-group mb-2">
            <input
              type="text"
              className="form-control"
              value={ingredient.name}
              onChange={(e) => handleIngredientChange(index, e.target.value)}
              required
            />
            <button
              type="button"
              className="btn btn-outline-danger"
              onClick={() => removeIngredient(index)}
              disabled={formData.ingredients.length === 1}
            >
              Remove
            </button>
          </div>
        ))}
        <button
          type="button"
          className="btn btn-outline-secondary"
          onClick={addIngredient}
        >
          Add Ingredient
        </button>
      </div>
      
      {/* More form fields... */}
      
      <button type="submit" className="btn btn-primary">
        {initialData ? 'Update Recipe' : 'Create Recipe'}
      </button>
    </form>
  );
};
```

### Deployment Pipeline
Successfully setting up the deployment pipeline for both the frontend and backend was a significant achievement. I configured Heroku for the Django backend and Netlify for the React frontend, with environment variables for different environments.

## Key Learnings/Takeaways

### Django REST Framework
This project significantly improved my understanding of Django REST Framework. I learned how to create complex API endpoints with nested serializers, implement token authentication, and handle file uploads. I'm now comfortable with creating custom permissions and serializer methods to meet specific requirements.

### React State Management
I gained valuable experience in managing state in a React application. Using context for global state like authentication and local state for component-specific data helped me create a maintainable and scalable frontend application.

### Full-Stack Integration
The most valuable learning was understanding how to integrate the frontend and backend effectively. I learned how to structure API endpoints to provide the data needed by the frontend components and how to handle authentication across the full stack.

### Deployment and DevOps
I gained practical experience in deploying both frontend and backend applications to production environments. Setting up environment variables, configuring databases, and implementing cloud storage for media files were all valuable skills I developed during this project.

## Bugs
- The recipe image upload occasionally fails on mobile devices due to file size limitations.
- Some users have reported issues with the password reset functionality not sending emails consistently.
- The recipe filtering system sometimes returns duplicate results when multiple filters are applied.

## Future Improvements

### Feature Enhancements
- Implement a meal planning feature that allows users to schedule recipes for specific days
- Add a shopping list generator based on selected recipes
- Implement a recipe recommendation system based on user preferences and past interactions
- Add social sharing capabilities for recipes

### Technical Improvements
- Implement server-side rendering for improved SEO and initial load performance
- Add comprehensive unit and integration tests for both frontend and backend
- Implement real-time notifications for comments and ratings using WebSockets
- Optimize image loading with lazy loading and responsive images
- Implement a more robust caching strategy for frequently accessed data
