# GitHub Deployment Guide for Savora Recipe App

This guide will walk you through setting up GitHub repositories for your Savora Recipe App and configuring deployments from GitHub to Netlify and Heroku.

## 1. Setting Up GitHub Repositories

You have two options:

1. Create separate repositories for frontend and backend (recommended)
2. Create a single repository with both projects

### Option 1: Separate Repositories (Recommended)

#### Backend Repository

1. Create a new repository on GitHub:

   - Go to https://github.com/new
   - Name: `savora-backend` (or your preferred name)
   - Choose public or private
   - Click "Create repository"

2. Initialize and push your backend code:
   ```bash
   # In your backend directory
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/savora-backend.git
   git push -u origin main
   ```

#### Frontend Repository

1. Create another repository on GitHub:

   - Go to https://github.com/new
   - Name: `savora-frontend` (or your preferred name)
   - Choose public or private
   - Click "Create repository"

2. Initialize and push your frontend code:
   ```bash
   # In your frontend directory
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/savora-frontend.git
   git push -u origin main
   ```

### Option 2: Single Repository

1. Create a new repository on GitHub:

   - Go to https://github.com/new
   - Name: `savora-recipe-app` (or your preferred name)
   - Choose public or private
   - Click "Create repository"

2. Organize your project structure:

   ```
   savora-recipe-app/
   ├── backend/
   │   └── (all backend files)
   ├── frontend/
   │   └── (all frontend files)
   └── README.md
   ```

3. Initialize and push your code:
   ```bash
   # In your project root directory
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/savora-recipe-app.git
   git push -u origin main
   ```

## 2. Deploying Backend to Heroku from GitHub

1. Create a new Heroku app:

   - Go to https://dashboard.heroku.com/new-app
   - Choose a name for your app
   - Click "Create app"

2. Connect to GitHub:

   - In your Heroku app dashboard, go to the "Deploy" tab
   - Select "GitHub" as the deployment method
   - Connect to your GitHub account if not already connected
   - Search for your backend repository and click "Connect"

3. Configure automatic deploys:

   - Scroll down to the "Automatic deploys" section
   - Choose the branch you want to deploy (usually `main`)
   - Optionally, select "Wait for CI to pass before deploy" if you have CI set up
   - Click "Enable Automatic Deploys"

4. Configure environment variables:

   - Go to the "Settings" tab
   - Click "Reveal Config Vars"
   - Add the following variables:
     - `SECRET_KEY`: Your Django secret key
     - `DEBUG`: "False"
     - `ALLOWED_HOSTS`: "your-app-name.herokuapp.com,localhost,127.0.0.1"
     - `CORS_ALLOWED_ORIGINS`: "https://your-netlify-app.netlify.app,http://localhost:5173"
     - `DATABASE_URL`: Your Neon database connection string

5. Manually deploy for the first time:

   - Go back to the "Deploy" tab
   - Scroll down to "Manual deploy"
   - Select your branch and click "Deploy Branch"

6. Run migrations and create a superuser:
   - In the Heroku dashboard, go to "More" > "Run console"
   - Run the following commands:
     ```
     python manage.py migrate
     python manage.py createsuperuser
     python manage.py seed_recipes --count 50  # Optional
     ```

## 3. Deploying Frontend to Netlify from GitHub

1. Create a new site on Netlify:

   - Go to https://app.netlify.com/
   - Click "Add new site" > "Import an existing project"
   - Select "GitHub" as the Git provider
   - Authorize Netlify to access your GitHub account if needed
   - Select your frontend repository

2. Configure build settings:

   - Build command: `npm run build`
   - Publish directory: `dist`
   - Click "Deploy site"

3. Configure environment variables:

   - Go to Site settings > Build & deploy > Environment
   - Click "Edit variables"
   - Add the environment variable:
     - Key: `VITE_API_URL`
     - Value: `https://your-heroku-app-name.herokuapp.com`
   - Click "Save"

4. Trigger a new build:
   - Go to the "Deploys" tab
   - Click "Trigger deploy" > "Deploy site"

## 4. Continuous Deployment Workflow

With GitHub deployment set up, your workflow becomes:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push
   ```
3. Automatic deployment:
   - Heroku will automatically deploy your backend
   - Netlify will automatically build and deploy your frontend

## 5. Troubleshooting GitHub Deployments

### Heroku Deployment Issues

- Check build logs in the Heroku dashboard
- Ensure your `Procfile` and `requirements.txt` are in the root of your repository
- Verify that your GitHub repository has the correct branch selected for deployment

### Netlify Deployment Issues

- Check build logs in the Netlify dashboard
- Ensure your `netlify.toml` file is in the root of your frontend repository
- Verify that environment variables are correctly set
- Check that the build command and publish directory are correctly configured

## 6. Additional GitHub Features

### GitHub Actions for CI/CD

You can set up GitHub Actions for continuous integration and testing:

1. Create a `.github/workflows` directory in your repository
2. Add workflow files for testing and linting
3. Configure Heroku and Netlify to wait for CI checks before deploying

### Branch Protection Rules

Set up branch protection rules to ensure code quality:

1. Go to your repository settings > Branches
2. Add a rule for your main branch
3. Require pull request reviews before merging
4. Require status checks to pass before merging
