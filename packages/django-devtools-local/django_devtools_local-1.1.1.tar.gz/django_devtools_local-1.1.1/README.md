# 🔧 Django DevTools

A complete Django development tools package, allowing you to explore the database, run Python/SQL code, and test functions in development mode.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-3.2%2B%20%7C%205.x-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange)](https://github.com/Prince-devC/django-devtools)

## ✨ Features

- 🗃️ **Model Exploration**: Automatic visualization of all Django models
- 📊 **Data View**: Paginated browsing of table contents with search
- 🐍 **Python Console**: Live Python code execution with access to the Django ORM
- 🗄️ **SQL Console**: Raw SQL query execution
- 🔍 **Database Schema**: Visualization of the complete database structure
- ⚙️ **Function Testing**: Interface for testing your apps' utility functions
- 🔒 **Enhanced Security**: Restricted access to DEBUG mode and superusers
- 📱 **Responsive Interface**: Modern design with Bootstrap 5

## 📋 Requirements

- **Python**: 3.8+ (3.10+ recommended for Django 5.x)
- **Django**: 3.2+ | 4.x | 5.x
- **Database**: MySQL, PostgreSQL, SQLite, Oracle supported
- **Browser**: Modern browsers (Chrome, Firefox, Safari, Edge)

## 🚀 Installation

### Installation via pip (recommended)
```bash
pip install django-devtools-local
```

### Installation from sources

```bash
git clone https://github.com/yourusername/django-devtools.git
cd django-devtools
pip install -e .
```

## ⚙️ Configuration

### 1. Adding to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # ... your other apps
    'devtools',
]
```

### 2. Configuring URLs

```python
# urls.py (main project)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # ... your other URLs
]

# Adding DevTools only in DEBUG mode
if settings.DEBUG:
    urlpatterns += [
        path('devtools/', include('devtools.urls')),
    ]
```

### 3. Optional Configuration

```python
# settings.py

# Allowed IP addresses for DevTools (default: localhost only)
DEVTOOLS_ALLOWED_IPS = [
    '127.0.0.1',
    '::1',
    # Add more IP addresses if needed
]

# Optional middleware for enhanced security
MIDDLEWARE = [
    # ... your other middleware
    'devtools.middleware.DevToolsSecurityMiddleware',  # Optional
]
```

## 🎯 Usage

### Accessing DevTools

1. Ensure `DEBUG = True` in your settings
2. Log in with a superuser account
3. Go to `http://localhost:8000/devtools/`

### Navigation

- **Home**: Overview of models and statistics
- **Tables**: Exploring data with Pagination and Search
- **Console**: Live Python/SQL Code Execution
- **Schema**: Database Structure Visualization
- **Functions**: Test Your Application's Utility Functions

### Usage Examples

#### Python Console
```python
# List all users
from django.contrib.auth.models import User
users = User.objects.all()
for user in users:
    print(f"{user.username} - {user.email}")

# Model Statistics
for app in apps.get_app_configs():
    for model in app.get_models():
        count = model.objects.count()
        print(f"{model.__name__}: {count} objects")
```

#### SQL Console
```sql
-- Analysis Queries
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = DATABASE()
ORDER BY table_rows DESC;

-- User statistics
SELECT COUNT(*) as total_users, 
       COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users
FROM auth_user;
```

## 🔒 Security

### Access Restrictions

DevTools applies several levels of security:

1. **DEBUG Mode Required**: Works only with `DEBUG = True`
2. **Authentication**: Only logged-in users can access
3. **Superuser Privileges**: Only superusers have access
4. **IP Whitelisting**: Restricted by IP address (localhost by default)

### Enhanced Security Configuration

```python
# settings.py
# For maximum security
DEVTOOLS_ALLOWED_IPS = ['127.0.0.1']  # Localhost only

# Adding security middleware
MIDDLEWARE = [
    # ... other middleware
    'devtools.middleware.DevToolsSecurityMiddleware',
]
```

## 🎨 Customization

### Custom CSS

Create a custom CSS file:

```css
/* static/css/devtools-custom.css */
:root { 
    --devtools-primary: #your-color;
}

.devtools-custom {
    /* Your custom styles */
}
```

### Custom Templates

You can override templates by creating:

```
your_app/templates/devtools/
├── base.html
├── index.html
├── tables.html
└── query.html
```

## 📷 Screenshots

### Dashboard Overview
![Dashboard](docs/images/dashboard.png)

### Python Console
![Console](docs/images/console.png)

### Database Schema
![Schema](docs/images/schema.png)

## 🛠️ Development

### Project Structure

```
django-devtools/
├── devtools/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── views.py
│   ├── urls.py
│   ├── utils.py
│   ├── middleware.py
│   ├── templates/devtools/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── tables.html
│   │   ├── query.html
│   │   ├── schema.html
│   │   └── functions.html
│   ├── static/devtools/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templatetags/
│       └── devtools_extras.py
├── setup.py
├── LICENSE
└── README.md
```

### Local Development Setup

```bash
# Clone the project
git clone https://github.com/yourusername/django-devtools.git
cd django-devtools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run tests
python -m pytest tests/

# Create example Django project for testing
django-admin startproject testproject
cd testproject
# Add 'devtools' to INSTALLED_APPS
# Configure URLs
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
pip install pytest-cov
python -m pytest --cov=devtools

# Run specific test file
python -m pytest tests/test_views.py
```

## 🐛 Troubleshooting

### Common Issues

#### DevTools not accessible
- ✅ Ensure `DEBUG = True` in settings
- ✅ Check that you're logged in as a superuser
- ✅ Verify URLs are properly configured
- ✅ Check IP whitelist settings

#### Permission denied errors
- ✅ Verify user has superuser privileges
- ✅ Check IP address is in DEVTOOLS_ALLOWED_IPS
- ✅ Ensure proper middleware configuration

#### Database connection errors
- ✅ Verify database configuration
- ✅ Check database permissions
- ✅ Ensure proper database drivers are installed

#### JavaScript/CSS not loading
- ✅ Run `python manage.py collectstatic`
- ✅ Verify static files configuration
- ✅ Check browser console for errors

## 📊 Performance Considerations

- DevTools are designed for **development only**
- SQL queries are executed directly - use with caution on large datasets
- Python code execution has built-in safety measures but runs in the main process
- Consider using pagination for large result sets
- Monitor memory usage when working with large datasets

## 🔄 Version Compatibility

| Django DevTools | Django Version | Python Version | Notes |
|-----------------|----------------|----------------|-------|
| 1.0.0           | 3.2.x          | 3.8+           | LTS Support |
| 1.0.0           | 4.0.x          | 3.8+           | ✅ Tested |
| 1.0.0           | 4.1.x          | 3.8+           | ✅ Tested |
| 1.0.0           | 4.2.x          | 3.8+           | LTS Support |
| 1.0.0           | 5.0.x          | 3.10+          | ✅ Compatible |
| 1.0.0           | 5.1.x          | 3.10+          | ✅ Compatible |

> **Note**: Django 5.x requires Python 3.10+. For Python 3.8-3.9, use Django 4.2 LTS.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use Black for code formatting
- Add docstrings to all functions and classes
- Write tests for new features

### Testing

```bash
# Run the full test suite
python -m pytest

# Check code style
black --check devtools/
flake8 devtools/

# Type checking
mypy devtools/
```

## ❓ FAQ

### Can I use DevTools in production?
**No!** DevTools are strictly for development environments. They provide powerful access to your database and Django internals.

### How do I add custom functions to test?
Create a `utils.py` file in your Django app with your functions. DevTools will automatically discover them.

### Can I customize the interface?
Yes! You can override templates and add custom CSS. See the Customization section.

### Is my data safe?
DevTools include multiple security layers, but should only be used in development environments with trusted users.

### What databases are supported?
DevTools work with any Django-supported database: PostgreSQL, MySQL, SQLite, Oracle.

### Is Django 5.x supported?
**Yes!** DevTools are fully compatible with Django 5.0 and 5.1. Note that Django 5.x requires Python 3.10+, while older Django versions support Python 3.8+.

## 📜 Changelog

### v1.0.0 (2024-01-XX)
- 🎉 Initial release
- ✨ Model exploration and data viewing
- ✨ Python/SQL console
- ✨ Database schema visualization
- ✨ Function testing interface
- 🔒 Security middleware and IP whitelisting
- 📱 Responsive Bootstrap 5 interface
- ⬆️ **Django 5.x Support**: Full compatibility with Django 5.0 and 5.1
- 🐍 **Python 3.12**: Support for latest Python version

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors & Credits

- **Main Developer**: [Your Name](https://github.com/yourusername)
- **Contributors**: [Contributors](https://github.com/yourusername/django-devtools/contributors)

### Acknowledgments

- Thanks to the Django community for the excellent framework
- Bootstrap team for the UI components
- All contributors and testers

## 📞 Support

### Getting Help

- 📖 **Documentation**: Read this README and inline documentation
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Prince-devC/django-devtools/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/Prince-devC/django-devtools/discussions)
- 💬 **Community**: [Django DevTools Discord](https://discord.gg/your-discord)

### Reporting Issues

When reporting issues, please include:

1. Django DevTools version
2. Django version
3. Python version
4. Database type and version
5. Error message and traceback
6. Steps to reproduce

### Professional Support

For commercial support or custom development:
- 📧 Email: prince.gnangnon2@gmail.com
- 🌐 Website: https://yourcompany.com/django-devtools

---

**⭐ If you find Django DevTools useful, please star the repository on GitHub!**

**🔧 Django DevTools** - Making Django development more productive and enjoyable! 🚀
