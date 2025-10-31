"""
Django settings for omeiat project.
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url
from django.contrib.messages import constants as messages

# ----------------------
# Paths
# ----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------
# Security
# ----------------------
SECRET_KEY = config("SECRET_KEY", default="insecure-secret-key")
DEBUG = config("DEBUG", default=True, cast=bool)  # Set to True for development
ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    default="localhost 127.0.0.1 [::1]"
).split()

# ----------------------
# Static Files Configuration (FIXED)
# ----------------------
STATIC_URL = '/static/'  # This must be defined
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For production
STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',  # Your actual static files location
]


# Media files configuration
MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# ----------------------
# Installed Apps
# ----------------------
INSTALLED_APPS = [
    'jazzmin',
    'app',
    'django_filters',
    'rest_framework',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',  # This app requires STATIC_URL
]

# ----------------------
# Middleware
# ----------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.middleware.InstitutionMiddleware',
]


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----------------------
# URL and WSGI
# ----------------------
ROOT_URLCONF = 'omeiat.urls'
WSGI_APPLICATION = 'omeiat.wsgi.application'

# ----------------------
# Templates
# ----------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "app" / "jobs" / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.theme_context',
            ],
        },
    },
]

# ----------------------
# Authentication
# ----------------------
AUTH_USER_MODEL = 'app.User'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# ----------------------
# Messages
# ----------------------
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# ----------------------
# Database
# ----------------------
if os.environ.get('GITHUB_ACTIONS') == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'omeiat_db',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('MYSQL_DATABASE', 'omeiat_db'),
            'USER': config('MYSQL_USER', 'root'),
            'PASSWORD': config('MYSQL_PASSWORD', 'root'),
            'HOST': config('MYSQL_HOST', 'localhost'),
            'PORT': config('MYSQL_PORT', '3306'),
        }
    }

# ----------------------
# Password Validation
# ----------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------
# Internationalization
# ----------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------
# Default primary key field type
# ----------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ----------------------
# Email (Gmail)
# ----------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ----------------------
# Crispy Forms
# ----------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ----------------------
# Jazzmin Admin
# ----------------------
JAZZMIN_SETTINGS = {
    "site_title": "Omeiat Admin",
    "site_header": "Omeiat Dashboard",
    "site_brand": "Omeiat",
    "site_logo": "app/images/logo.png",
    "welcome_sign": "Welcome to the Omeiat Admin",
    "copyright": "Omeiat © 2025",
    "theme": "cerulean",
    "show_sidebar": True,
    "navigation_expanded": True,
}

# ----------------------
# Security (Production)
# ----------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'