# OJT Certificate Verification System - Deployment Guide

This guide explains how to deploy your OJT Certificate Verification application using free hosting options with custom domain support.

## Option 1: Deploy on Replit (Recommended)

Replit offers a simple, free way to host your Flask application.

### Basic Deployment:
1. Make sure your project is working locally on Replit
2. Click the "Deploy" button in the top-right corner of Replit
3. Follow the prompts to deploy your application
4. Your application will be available at a `[username].[project-name].repl.co` URL

### Custom Domain Setup with Replit:
1. Upgrade to Replit Pro (affordable option) or Teams
2. Go to your deployed app settings
3. Click on "Custom Domains"
4. Add your domain name
5. Configure the DNS records at your domain registrar:
   - Add a CNAME record pointing to your Replit app URL
   - Example: `CNAME www -> yourusername-projectname.repl.co`

**Benefits of Replit Deployment:**
- Zero configuration needed
- Automatic HTTPS
- Free tier available (with subdomain)
- Custom domains with paid plans

## Option 2: Deploy on PythonAnywhere

PythonAnywhere offers a free tier that works well for Flask applications.

### Basic Deployment:
1. Sign up for a free account at [PythonAnywhere](https://www.pythonanywhere.com/)
2. Upload your project files (use Git or the file uploader)
3. Set up a new web app:
   - Select "Flask" as your framework
   - Configure WSGI file to point to your app
   - Set up your virtual environment
4. Your app will be available at `[username].pythonanywhere.com`

### Custom Domain Setup with PythonAnywhere:
1. Upgrade to a paid plan (Web Developer or higher)
2. Go to the Web tab in your PythonAnywhere dashboard
3. Under "Configuration" for your web app, click "Add a custom domain"
4. Add your domain name
5. Configure your domain's DNS:
   - Add a CNAME record pointing to `www.[username].pythonanywhere.com`
   - Or an A record pointing to the provided IP address

**Benefits of PythonAnywhere:**
- Easy setup for Python/Flask applications
- Free tier available (with subdomain)
- Custom domains with paid plans
- Includes a MySQL database

## Option 3: Deploy on Render

Render offers a generous free tier for web services.

### Basic Deployment:
1. Sign up at [Render](https://render.com/)
2. Connect your GitHub/GitLab repository or upload your files
3. Create a new Web Service
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `gunicorn main:app`
6. Your app will be available at a `[project-name].onrender.com` URL

### Custom Domain Setup with Render:
1. Free tier supports custom domains!
2. Go to your deployed web service dashboard
3. Click on "Settings" and then "Custom Domain"
4. Add your domain name
5. Configure your domain's DNS:
   - Add a CNAME record pointing to `[project-name].onrender.com`
6. Render will automatically provision an SSL certificate for your domain

**Benefits of Render:**
- Generous free tier
- Automatic HTTPS
- Custom domains on free tier
- Easy deployment from GitHub/GitLab
- Auto-deploys when you push changes

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

## Free Deployment with Custom Domain (Summary)

Here's a quick comparison of the options that offer free deployment with custom domain support:

| Platform | Free Tier w/ Custom Domain | HTTPS | Deployment Difficulty |
|----------|----------------------------|-------|------------------------|
| Render   | ✅ Yes                     | ✅ Yes | Easy                   |
| Vercel   | ✅ Yes                     | ✅ Yes | Easy                   |
| Netlify  | ✅ Yes (with limitations)  | ✅ Yes | Easy                   |
| Replit   | ❌ Requires paid plan      | ✅ Yes | Very Easy              |
| PythonAnywhere | ❌ Requires paid plan | ✅ Yes | Moderate              |

**Best Free Option:** Render is highly recommended as it offers custom domains on its free tier with automatic HTTPS.

## Additional Free Option: Vercel

Vercel also offers an excellent free tier with custom domain support:

1. Sign up at [Vercel](https://vercel.com/)
2. Connect your GitHub/GitLab repository
3. Configure the build settings:
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `./`
   - Install Command: `pip install -r requirements.txt`
4. Add your custom domain in the Vercel dashboard
5. Configure your domain's DNS with the provided instructions

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