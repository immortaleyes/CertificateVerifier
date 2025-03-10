# Deployment Requirements

When deploying your OJT Certificate Verification System to a hosting platform, make sure to include the following dependencies:

```
flask==2.3.3
flask-sqlalchemy==3.1.1
gunicorn==23.0.0
openpyxl==3.1.2
pandas==2.1.1
werkzeug==2.3.7
email-validator==2.0.0
```

## Installation

On most platforms, you can install these requirements using:

```bash
pip install -r requirements.txt
```

Or manually install each dependency:

```bash
pip install flask==2.3.3 flask-sqlalchemy==3.1.1 gunicorn==23.0.0 openpyxl==3.1.2 pandas==2.1.1 werkzeug==2.3.7 email-validator==2.0.0
```

## Important Files to Include

When deploying, make sure your project includes:

1. All Python files (app.py, main.py)
2. Templates directory with all HTML files
3. Static directory with CSS and JavaScript
4. Data files:
   - Excel file with student records
   - ZIP file with certificates

## Starting the Application

Most hosting platforms will require a command to start your application. Use:

```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port main:app
```

Or if the platform uses a Procfile:

```
web: gunicorn main:app
```

## Environment Variables

For production environments, set these environment variables:

- SESSION_SECRET - A random, secure string for session encryption