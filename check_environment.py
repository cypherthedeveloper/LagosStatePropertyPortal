#!/usr/bin/env python
"""
Environment Checker for Lagos State Property Portal

This script checks your environment for compatibility with the Lagos State Property Portal
and helps diagnose common installation issues.

Usage:
    python check_environment.py
"""

import os
import sys
import platform
import subprocess
import importlib.util
from pathlib import Path

# Required Python version
MIN_PYTHON_VERSION = (3, 8)

# Required packages from requirements.txt
REQUIRED_PACKAGES = [
    'django',
    'djangorestframework',
    'mysqlclient',
    'pillow',
    'python-dotenv',
    'python-decouple',
    'drf-spectacular',
    'django-cors-headers',
    'django-filter',
    'djangorestframework-simplejwt',
    'requests',
    'boto3',
]

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Check if we're running on Windows (for color support)
IS_WINDOWS = platform.system() == 'Windows'

def print_colored(text, color):
    """Print colored text if supported by the terminal"""
    if IS_WINDOWS:
        print(text)
    else:
        print(f"{color}{text}{Colors.ENDC}")

def print_header(text):
    """Print a header"""
    print("\n" + "=" * 80)
    print_colored(text, Colors.HEADER + Colors.BOLD)
    print("=" * 80)

def print_success(text):
    """Print a success message"""
    print_colored(f"✓ {text}", Colors.OKGREEN)

def print_warning(text):
    """Print a warning message"""
    print_colored(f"⚠ {text}", Colors.WARNING)

def print_error(text):
    """Print an error message"""
    print_colored(f"✗ {text}", Colors.FAIL)

def print_info(text):
    """Print an info message"""
    print_colored(f"ℹ {text}", Colors.OKBLUE)

def check_python_version():
    """Check if Python version meets requirements"""
    print_header("Checking Python Version")
    current_version = sys.version_info
    print_info(f"Current Python version: {sys.version}")
    
    if current_version >= MIN_PYTHON_VERSION:
        print_success(f"Python version {current_version.major}.{current_version.minor} meets the minimum requirement of {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}")
        return True
    else:
        print_error(f"Python version {current_version.major}.{current_version.minor} does not meet the minimum requirement of {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}")
        print_info(f"Please upgrade your Python version to {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} or higher")
        return False

def check_virtual_env():
    """Check if running in a virtual environment"""
    print_header("Checking Virtual Environment")
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if in_venv:
        print_success("Running in a virtual environment")
        print_info(f"Virtual environment path: {sys.prefix}")
        return True
    else:
        print_warning("Not running in a virtual environment")
        print_info("It's recommended to use a virtual environment for this project")
        print_info("Create one with: python -m venv venv")
        print_info("Activate it with: source venv/bin/activate (Linux/macOS) or venv\Scripts\activate (Windows)")
        return False

def check_packages():
    """Check if required packages are installed"""
    print_header("Checking Required Packages")
    missing_packages = []
    outdated_packages = []
    
    for package in REQUIRED_PACKAGES:
        spec = importlib.util.find_spec(package.replace('-', '_'))
        if spec is None:
            print_error(f"Package '{package}' is not installed")
            missing_packages.append(package)
        else:
            try:
                module = importlib.import_module(package.replace('-', '_'))
                version = getattr(module, '__version__', 'unknown')
                print_success(f"Package '{package}' is installed (version: {version})")
            except (ImportError, AttributeError):
                print_success(f"Package '{package}' is installed")
    
    if missing_packages:
        print_warning(f"Missing packages: {', '.join(missing_packages)}")
        print_info("Install them with: pip install -r requirements.txt")
        return False
    else:
        print_success("All required packages are installed")
        return True

def check_mysql():
    """Check MySQL connection"""
    print_header("Checking MySQL")
    
    try:
        import MySQLdb
        print_success("MySQLdb module is installed")
        
        # Check if we can import the mysqlclient package
        try:
            import mysqlclient
            print_success("mysqlclient package is installed")
        except ImportError:
            pass  # This is expected, as mysqlclient is the package name but not the import name
        
        # Try to get the version
        try:
            version = MySQLdb.get_client_info()
            print_info(f"MySQL client version: {version}")
        except Exception as e:
            print_warning(f"Could not get MySQL client version: {e}")
        
        return True
    except ImportError:
        print_error("MySQLdb module is not installed correctly")
        print_info("This could indicate issues with the mysqlclient package")
        
        # Check for common MySQL installation issues
        if platform.system() == 'Windows':
            print_info("On Windows, you might need to install Visual C++ Build Tools")
            print_info("Try: pip install --only-binary :all: mysqlclient")
        elif platform.system() == 'Linux':
            print_info("On Linux, you might need to install: python3-dev default-libmysqlclient-dev build-essential")
        elif platform.system() == 'Darwin':  # macOS
            print_info("On macOS, you might need to install MySQL with: brew install mysql")
        
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Checking Environment File")
    
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if not env_path.exists():
        print_error(".env file not found")
        
        if env_example_path.exists():
            print_info(".env.example file found")
            print_info("Copy .env.example to .env and update the values")
        else:
            print_error(".env.example file not found")
            print_info("Create a .env file with the required variables (see README.md)")
        
        return False
    
    print_success(".env file found")
    
    # Check for required variables
    required_vars = [
        'SECRET_KEY',
        'DEBUG',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT',
    ]
    
    missing_vars = []
    with open(env_path, 'r') as f:
        env_content = f.read()
        
        for var in required_vars:
            if not any(line.strip().startswith(f"{var}=") for line in env_content.splitlines()):
                missing_vars.append(var)
    
    if missing_vars:
        print_warning(f"Missing environment variables: {', '.join(missing_vars)}")
        print_info("Add these variables to your .env file")
        return False
    else:
        print_success("All required environment variables found")
        return True

def check_database_connection():
    """Check if we can connect to the database"""
    print_header("Checking Database Connection")
    
    try:
        # Try to import Django settings to get database configuration
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        
        try:
            from django.conf import settings
            db_settings = settings.DATABASES['default']
            print_info(f"Database engine: {db_settings['ENGINE']}")
            print_info(f"Database name: {db_settings['NAME']}")
            print_info(f"Database host: {db_settings['HOST']}")
            print_info(f"Database port: {db_settings['PORT']}")
            
            # Try to connect to the database
            try:
                import MySQLdb
                conn = MySQLdb.connect(
                    host=db_settings['HOST'],
                    user=db_settings['USER'],
                    passwd=db_settings['PASSWORD'],
                    db=db_settings['NAME'],
                    port=int(db_settings['PORT'])
                )
                print_success("Successfully connected to the database")
                conn.close()
                return True
            except Exception as e:
                print_error(f"Could not connect to the database: {e}")
                print_info("Check your database credentials in the .env file")
                print_info("Make sure the MySQL server is running")
                return False
        except Exception as e:
            print_error(f"Could not load Django settings: {e}")
            return False
    except Exception as e:
        print_error(f"Error checking database connection: {e}")
        return False

def main():
    """Run all checks"""
    print_header("Lagos State Property Portal Environment Checker")
    print_info("This script will check your environment for compatibility with the project")
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("Required Packages", check_packages),
        ("MySQL Installation", check_mysql),
        ("Environment File", check_env_file),
        ("Database Connection", check_database_connection),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print_error(f"Error during {name} check: {e}")
            results[name] = False
    
    # Print summary
    print_header("Summary")
    all_passed = True
    for name, result in results.items():
        if result:
            print_success(f"{name}: Passed")
        else:
            print_error(f"{name}: Failed")
            all_passed = False
    
    if all_passed:
        print_header("All checks passed! Your environment is ready for the Lagos State Property Portal.")
    else:
        print_header("Some checks failed. Please fix the issues before proceeding.")
        print_info("Refer to the INSTALLATION_TROUBLESHOOTING.md file for help")

if __name__ == "__main__":
    main()