# Buzzerboy Platform Connectors

[![Version](https://img.shields.io/badge/version-0.0.9-blue.svg)](https://pypi.org/project/buzzerboy-platform-connectors/)
[![Python](https://img.shields.io/badge/python->=3.8-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## Overview

Buzzerboy Platform Connectors is a Python utility library that parses integration JSON configurations into usable Django settings keys. This package simplifies the management of sensitive configuration data by providing a unified interface to access secrets from environment variables or JSON-encoded secret strings.

The library is designed specifically for Django applications that need to securely manage database connections, email configurations, and other platform integrations while supporting both environment variable and JSON-based secret management strategies. The package has been recently restructured with enhanced automation capabilities through the new `BuzzerboyPlatformConnector` module.

## Features

- **Dual Configuration Sources**: Supports both environment variables and JSON-encoded secret strings
- **Django Integration**: Provides ready-to-use configuration values for Django settings
- **Database Configuration**: Simplified database connection setup (host, port, user, password, engine)
- **Email Configuration**: Complete email backend configuration management
- **URL Processing**: Utilities for handling HTTP/HTTPS prefixes and CSRF hosts
- **Package Automation**: Advanced package management with automated versioning and changelog generation
- **Security First**: Designed with secure secret management principles

## Installation

### From PyPI (when available)
```bash
pip install buzzerboy-platform-connectors
```

## Quick Start

### Basic Usage

```python
from PlatformConnectors import PlatformConnectors as pc

# Database configuration
db_config = {
    'ENGINE': pc.getDBEngine('django.db.backends.postgresql'),
    'NAME': pc.getDBName(),
    'USER': pc.getDBUser(),
    'PASSWORD': pc.getDBPassword(),
    'HOST': pc.getDBHost('localhost'),
    'PORT': pc.getDBPort('5432'),
}

# Email configuration
email_config = {
    'EMAIL_BACKEND': pc.getEmailBackend(),
    'EMAIL_HOST': pc.getEmailHost(),
    'EMAIL_PORT': pc.getEmailPort(587),
    'EMAIL_HOST_USER': pc.getEmailUser(),
    'EMAIL_HOST_PASSWORD': pc.getEmailPassword(),
    'EMAIL_USE_TLS': pc.getEmailUseTLS(True),
    'DEFAULT_FROM_EMAIL': pc.getEmailDefaultFromEmail(),
}
```

### Using with Django Settings

```python
# settings.py
from PlatformConnectors import PlatformConnectors as pc
from PlatformConnectors import PlatformHelpers as ph

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': pc.getDBEngine('django.db.backends.postgresql'),
        'NAME': pc.getDBName(),
        'USER': pc.getDBUser(),
        'PASSWORD': pc.getDBPassword(),
        'HOST': pc.getDBHost('localhost'),
        'PORT': pc.getDBPort('5432'),
    }
}

# Email Configuration
EMAIL_BACKEND = pc.getEmailBackend()
EMAIL_HOST = pc.getEmailHost()
EMAIL_PORT = int(pc.getEmailPort(587))
EMAIL_HOST_USER = pc.getEmailUser()
EMAIL_HOST_PASSWORD = pc.getEmailPassword()
EMAIL_USE_TLS = pc.getEmailUseTLS(True)
DEFAULT_FROM_EMAIL = pc.getEmailDefaultFromEmail()

# CORS and CSRF Configuration
ALLOWED_HOSTS = ph.allowHostCSVtoArray(os.environ.get('ALLOWED_HOSTS', 'localhost'))
CSRF_TRUSTED_ORIGINS = ph.getCSRFHostsFromAllowedHosts(ALLOWED_HOSTS)
```

## Configuration Methods

### Environment Variables

Set individual environment variables for each configuration value:

```bash
export dbname="myapp_db"
export username="db_user"
export password="secure_password"
export host="db.example.com"
export port="5432"
export engine="django.db.backends.postgresql"

export email_host="smtp.gmail.com"
export email_port="587"
export email_user="your-email@gmail.com"
export email_password="app-password"
export email_use_tls="True"
export email_backend="django.core.mail.backends.smtp.EmailBackend"
```

### JSON Secret String

Alternatively, provide all secrets in a single JSON-encoded environment variable:

```bash
export SECRET_STRING='{"dbname": "myapp_db", "username": "db_user", "password": "secure_password", "host": "db.example.com", "port": "5432", "engine": "django.db.backends.postgresql", "email_host": "smtp.gmail.com", "email_port": "587", "email_user": "your-email@gmail.com", "email_password": "app-password", "email_use_tls": true, "email_backend": "django.core.mail.backends.smtp.EmailBackend"}'
```

## API Reference

### Database Functions

| Function | Description | Default |
|----------|-------------|---------|
| `getDBName(default="")` | Database name | `""` |
| `getDBUser(default="")` | Database username | `""` |
| `getDBPassword(default="")` | Database password | `""` |
| `getDBHost(default="")` | Database host | `""` |
| `getDBPort(default="")` | Database port | `""` |
| `getDBEngine(default="")` | Database engine | `""` |

### Email Functions

| Function | Description | Default |
|----------|-------------|---------|
| `getEmailHost(default="")` | SMTP host | `""` |
| `getEmailPort(default="")` | SMTP port | `""` |
| `getEmailUser(default="")` | SMTP username | `""` |
| `getEmailPassword(default="")` | SMTP password | `""` |
| `getEmailUseTLS(default=True)` | Use TLS encryption | `True` |
| `getEmailDefaultFromEmail(default="")` | Default sender email | `""` |
| `getEmailBackend(default="django.core.mail.backends.console.EmailBackend")` | Email backend class | Console backend |

### Helper Functions

| Function | Description |
|----------|-------------|
| `addHttpPrefix(url)` | Adds HTTP/HTTPS prefixes to URLs |
| `removeHttpPrefix(url)` | Removes HTTP/HTTPS prefixes from URLs |
| `allowHostCSVtoArray(csvString)` | Converts CSV host string to array |
| `getCSRFHostsFromAllowedHosts(allowedHostsArray)` | Generates CSRF trusted origins from allowed hosts |

### Package Automation

The `PackageMaker` class provides automated package management functionality:

| Method | Description |
|--------|-------------|
| `PackageAutomation.auto_package()` | Automatically generates changelog, increments version, and creates package.json |
| `PackageAutomation.auto_setup()` | Automated setup.py configuration |
| `generate_changelog_from_git_log()` | Generates changelog from git commit history |
| `increment_version()` | Automatically increments package version |
| `generate_package_json()` | Creates package.json for semantic-release |

#### Usage:
```python
from PlatformConnectors.PackageMaker import PackageAutomation

# Automatic package management
package = PackageAutomation.auto_package()

# Or manual setup
automation = PackageAutomation()
automation.generate_changelog_from_git_log()
automation.increment_version()
automation.generate_package_json()
```

## Development

### Requirements

- Python >= 3.8
- toml

### Building the Package

The package now includes automated build tools:

```bash
# Using the new PackageMaker automation
python -c "from PlatformConnectors.PackageMaker import PackageAutomation; PackageAutomation.auto_package()"

# Traditional method
python setup.py sdist bdist_wheel
```

### Version Management

The package uses semantic versioning with enhanced automated version management through the `PackageMaker` class:

```bash
# Automated version management (recommended)
python -c "from PlatformConnectors.PackageMaker import PackageAutomation; PackageAutomation.auto_package()"

# Legacy method
python prepare.py
```

The new `PackageMaker` automation will:
- Generate a changelog from git commits
- Increment the version number intelligently
- Create/update package.json for semantic-release
- Handle MANIFEST.in requirements automatically


## Security Considerations

- **Never commit secrets**: Use environment variables or secure secret management
- **JSON Secret String**: When using `SECRET_STRING`, ensure it's properly secured in your deployment environment
- **Default Values**: Be cautious with default values in production environments

## Support

This package is internally managed by Buzzerboy Inc.

## License

Copyright (c) 2024 Buzzerboy Inc. Canada. All Rights Reserved.

This software is proprietary and available only for use within projects developed by Buzzerboy Inc. Canada. See [LICENSE](LICENSE) for full details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.
