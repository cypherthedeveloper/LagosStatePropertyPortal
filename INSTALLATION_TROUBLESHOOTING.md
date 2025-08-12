# Installation Troubleshooting Guide

## Common Installation Issues

If you're experiencing errors during the installation process, here are some common issues and their solutions:

### 1. MySQL Database Issues

The project uses MySQL as the database backend. Common errors include:

#### Error: `mysqlclient` installation fails

**Symptoms:**
- Error message about missing MySQL client libraries
- `error: command 'gcc' failed with exit status 1`

**Solutions:**

**Windows:**
- Install MySQL Server from the [official website](https://dev.mysql.com/downloads/mysql/)
- Make sure you have the Visual C++ Build Tools installed
- Try using a pre-compiled wheel:
  ```
  pip install --only-binary :all: mysqlclient
  ```

**Linux (Ubuntu/Debian):**
- Install required packages:
  ```
  sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
  ```

**macOS:**
- Install MySQL and required dependencies:
  ```
  brew install mysql
  ```

### 2. Environment Variables Issues

#### Error: Missing environment variables

**Symptoms:**
- `ImproperlyConfigured: Set the SECRET_KEY environment variable`
- Database connection errors

**Solutions:**
- Make sure you've created a `.env` file in the project root directory
- Copy all variables from `.env.example` to your `.env` file
- Update the values with your actual configuration
- Ensure the `.env` file is in the correct location (project root)

### 3. Python Version Issues

#### Error: Incompatible Python version

**Symptoms:**
- Syntax errors or import errors
- Package installation failures

**Solutions:**
- This project requires Python 3.8 or higher
- Verify your Python version:
  ```
  python --version
  ```
- If needed, install a compatible Python version

### 4. Virtual Environment Issues

#### Error: Packages not found after installation

**Symptoms:**
- `ModuleNotFoundError: No module named 'django'`
- Other missing package errors

**Solutions:**
- Make sure your virtual environment is activated
  - Windows: `venv\Scripts\activate`
  - macOS/Linux: `source venv/bin/activate`
- Verify that you see `(venv)` at the beginning of your command prompt
- Try reinstalling the requirements:
  ```
  pip install -r requirements.txt
  ```

### 5. Database Connection Issues

#### Error: Cannot connect to MySQL server

**Symptoms:**
- `django.db.utils.OperationalError: (2002, "Can't connect to MySQL server on 'localhost'")`
- Other database connection errors

**Solutions:**
- Ensure MySQL server is running
- Verify your database credentials in the `.env` file
- Make sure the database exists:
  ```
  mysql -u root -p
  CREATE DATABASE lagos_property_portal;
  ```
- Check if the MySQL user has proper permissions

### 6. Pillow Library Issues

#### Error: Pillow installation fails

**Symptoms:**
- Errors about missing image libraries or headers

**Solutions:**

**Windows:**
- Install Visual C++ Build Tools

**Linux (Ubuntu/Debian):**
- Install required packages:
  ```
  sudo apt-get install python3-dev libjpeg-dev libpng-dev
  ```

**macOS:**
- Install dependencies:
  ```
  brew install libjpeg libpng
  ```

## Still Having Issues?

If you're still experiencing installation problems after trying these solutions:

1. Check the Django and MySQL documentation for your specific operating system
2. Make sure all system dependencies are installed
3. Try creating a fresh virtual environment
4. Ensure you have the latest pip version: `pip install --upgrade pip`

For project-specific help, please open an issue on the project repository with details about your environment and the exact error messages you're seeing.