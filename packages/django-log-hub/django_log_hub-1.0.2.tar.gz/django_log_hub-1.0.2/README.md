# Django Log Hub

A reusable Django app for managing and viewing application logs with a beautiful web interface.

## Features

- 📊 **Log Viewer**: View and filter application logs in real-time
- 🔍 **Advanced Filtering**: Filter by log level, date range, status code, and custom keywords
- 📁 **File Management**: Download and clear log files
- 🎨 **Beautiful UI**: Modern Bootstrap-based interface
- 🔐 **Security**: Admin-only access with proper permissions
- ⚙️ **Configurable**: Customizable log directory and template paths
- 📦 **Reusable**: Easy to integrate into any Django project
- 🌍 **Internationalization**: Support for Turkish and English languages

## Installation

### From PyPI

```bash
pip install django-log-hub
```

### From Source

```bash
git clone https://github.com/eneshazr/django-log-hub.git
cd django-log-hub
pip install -e .
```

## Setup

1. **Add to INSTALLED_APPS** in your Django settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'log_hub',
]
```

2. **Configure logging** in your Django settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(name)s %(process)d %(thread)d %(message)s %(status_code)s %(taskName)s %(request)s',
        },
    },
    'handlers': {
        'file_info': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'info.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'file_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file_info', 'file_error'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.makedirs(os.path.join(BASE_DIR, 'logs'))
```

3. **Add URLs** to your main urls.py:

```python
from django.urls import path, include

urlpatterns = [
    # ... other URLs
    path('admin/logs/', include('log_hub.urls')),
]
```

4. **Run migrations** (if any):

```bash
python manage.py migrate
```

## Configuration

You can customize the app behavior using these settings:

```python
# Log Hub Configuration
LOG_HUB_LOG_DIR = os.path.join(BASE_DIR, 'logs')  # Log directory path
LOG_HUB_TEMPLATE = 'log_hub/logging.html'  # Custom template path

# Internationalization (i18n) Settings
LANGUAGE_CODE = 'en'  # Default language
LANGUAGES = [
    ('en', 'English'),
    ('tr', 'Türkçe'),
]
USE_I18N = True
USE_L10N = True

# Add LocaleMiddleware for language switching
MIDDLEWARE = [
    # ... other middleware
    'django.middleware.locale.LocaleMiddleware',  # Add this for language support
    # ... other middleware
]
```

## Usage

### Accessing the Log Hub

Navigate to `/admin/logs/` in your browser. You must be logged in as an admin user to access the logs.

### Features

- **Log File Selection**: Choose which log file to view
- **Filtering**: Filter logs by:
  - Log level (INFO, WARNING, ERROR)
  - Date range
  - Status code
  - Search keywords
  - Exclude keywords
- **File Management**:
  - Download log files
  - Clear log files
- **Real-time Viewing**: View logs in a beautiful accordion interface
- **Language Support**: Switch between Turkish and English interfaces

### API Endpoints

- `GET /logs/` - View logs with filtering
- `GET /logs/change-language/` - Change interface language
- `GET /logs/download/<filename>/` - Download log file
- `POST /logs/clear/<filename>/` - Clear log file

## Requirements

- Python 3.8+
- Django 3.2+
- python-json-logger 2.0+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

## Changelog

### 1.0.1
- Added Turkish language support
- Improved error handling with user-friendly messages
- Enhanced security with path traversal protection
- Added language switcher in UI
- Fixed CSRF protection issues
- Optimized log file reading performance
- Added comprehensive internationalization (i18n) support

### 1.0.0
- Initial release
- Log viewing and filtering
- File management (download/clear)
- Beautiful Bootstrap UI
- Admin-only access
