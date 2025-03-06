# Savora Recipe App Deployment Guide

This guide will walk you through deploying the Savora Recipe App with:

- Frontend on Netlify
- Backend on Heroku
- Database on Neon

## Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- [Netlify CLI](https://docs.netlify.com/cli/get-started/) (optional)
- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (v16 or higher)
- [Neon PostgreSQL](https://neon.tech/) account

## 1. Database Setup (Neon)

1. Create a Neon account at https://neon.tech/
2. Create a new project
   - When asked "Add this app to a pipeline?", select "No" for a simple setup
   - A pipeline is useful for more complex applications with staging/production environments, but not necessary for this project
3. Create a new database named `recipe_db`
4. Get your connection string from the Neon dashboard:
   - Go to the "Connection Details" tab
   - Select "PostgreSQL" connection
   - Copy the connection string that looks like: `postgres://user:password@hostname:port/dbname`
5. Save this connection string for later use with Heroku

## 2. Backend Deployment (Heroku)

1. Create a Heroku account at https://signup.heroku.com/
2. Install the Heroku CLI and login:

   ```
   heroku login
   ```

3. Create a new Heroku app:

   ```
   heroku create your-app-name
   ```

4. Add the PostgreSQL addon to your Heroku app:

   ```
   heroku addons:create heroku-postgresql:mini
   ```

5. Set environment variables:

   ```
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG="False"
   heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com,localhost,127.0.0.1"
   heroku config:set CORS_ALLOWED_ORIGINS="https://your-netlify-app.netlify.app,http://localhost:5173"
   heroku config:set DATABASE_URL="your-neon-connection-string"
   ```

6. Deploy to Heroku:

   ```
   git add .
   git commit -m "Prepare for deployment"
   git push heroku main
   ```

7. Run migrations:

   ```
   heroku run python manage.py migrate
   ```

8. Create a superuser:

   ```
   heroku run python manage.py createsuperuser
   ```

9. Seed the database (optional):
   ```
   heroku run python manage.py seed_recipes --count 50
   ```

## 3. Frontend Deployment (Netlify)

1. Create a Netlify account at https://app.netlify.com/signup
2. Update the `.env.production` file with your Heroku app URL:

   ```
   VITE_API_URL=https://your-app-name.herokuapp.com
   ```

3. Build the frontend:

   ```
   cd ../recipe-frontend
   npm install
   npm run build
   ```

4. Deploy to Netlify using the Netlify UI:

   - Go to https://app.netlify.com/
   - Drag and drop the `dist` folder from your local machine
   - Or connect your GitHub repository for continuous deployment

5. Configure your site settings:

   - Go to Site settings > Build & deploy > Environment
   - Add the environment variable:
     - Key: `VITE_API_URL`
     - Value: `https://your-app-name.herokuapp.com`

6. Set up redirects for SPA routing:
   - Netlify will use the `netlify.toml` file we created

## 4. Testing the Deployment

1. Visit your Netlify app URL
2. Try to register a new user
3. Create a new recipe
4. Test all features

## Troubleshooting

### Backend Issues

- Check Heroku logs:

  ```
  heroku logs --tail
  ```

- Verify environment variables:
  ```
  heroku config
  ```

### Frontend Issues

- Check Netlify deploy logs in the Netlify dashboard
- Verify that the API URL is correctly set in the environment variables
- Check browser console for any errors

## Maintenance

### Database Backups

- Neon provides automatic backups
- You can also manually backup your database:
  ```
  heroku pg:backups:capture
  ```

### Updating the Application

1. Make changes to your code
2. Test locally
3. Commit and push to Heroku for backend:
   ```
   git push heroku main
   ```
4. For frontend, rebuild and redeploy:
   ```
   npm run build
   ```
   Then upload to Netlify or push to your connected repository
