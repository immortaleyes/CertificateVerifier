# OJT Certificate Verification System - Deployment Guide

This guide explains how to deploy your OJT Certificate Verification application using free hosting options.

## Option 1: Deploy on Replit (Recommended)

Replit offers a simple, free way to host your Flask application.

1. Make sure your project is working locally on Replit
2. Click the "Deploy" button in the top-right corner of Replit
3. Follow the prompts to deploy your application
4. Your application will be available at a `[username].[project-name].repl.co` URL

**Benefits of Replit Deployment:**
- Zero configuration needed
- Automatic HTTPS
- Free tier available
- Custom domains possible with paid plans

## Option 2: Deploy on PythonAnywhere

PythonAnywhere offers a free tier that works well for Flask applications.

1. Sign up for a free account at [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload your project files (use Git or the file uploader)
3. Set up a new web app:
   - Select "Flask" as your framework
   - Configure WSGI file to point to your app
   - Set up your virtual environment
4. Your app will be available at `[username].pythonanywhere.com`

**Requirements for PythonAnywhere:**
- Ensure your app binds to `0.0.0.0` on port 5000
- Make sure your static files are properly configured

## Option 3: Deploy on Render

Render offers a generous free tier for web services.

1. Sign up at [Render](https://render.com/)
2. Connect your GitHub/GitLab repository or upload your files
3. Create a new Web Service
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `gunicorn main:app`
6. Your app will be available at a `[project-name].onrender.com` URL

## Preparing for Deployment (Any Platform)

Before deploying to any platform, make sure:

1. Create a `requirements.txt` file by running:
   ```
   pip freeze > requirements.txt
   ```

2. Make sure your file paths use relative paths, not absolute paths

3. Test your application locally to ensure it works properly

4. For security in production, set proper environment variables:
   ```python
   app.secret_key = os.environ.get("SESSION_SECRET", "default-only-for-development")
   ```

## Managing Certificate Data in Production

For deployment, you have several options for managing certificate data:

1. **Include in repository** - Fine for small, public data
2. **Cloud storage integration** - For larger datasets
3. **Database storage** - For scalable, searchable solutions

For your current setup, including the Excel and ZIP files in the repository is the simplest solution.

## Support and Troubleshooting

If you encounter issues during deployment:

1. Check the hosting platform's logs
2. Verify all dependencies are installed
3. Ensure file paths are correct for the deployed environment
4. Test with a simplified version of the application