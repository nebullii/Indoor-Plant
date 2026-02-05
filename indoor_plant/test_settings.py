"""
Test settings for Indoor Plant project.
Uses SQLite in-memory database and disables external service dependencies.
"""
import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'test-secret-key-not-for-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "accounts",
    "indoor_plant",
    'widget_tweaks',
    'products',
    'cart',
    'orders',
    'payments',
    'django_countries',
    'admin_dashboard',
    'ai',
    'analytics',
    'ckeditor',
    'django_quill',
    'inventory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "indoor_plant.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'products.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = "indoor_plant.wsgi.application"

# SQLite in-memory for fast tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

AUTH_USER_MODEL = 'accounts.CustomUser'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Stripe test keys
STRIPE_PUBLISHABLE_KEY = 'pk_test_fake'
STRIPE_SECRET_KEY = 'sk_test_fake'

# OpenAI test key
OPENAI_API_KEY = 'sk-test-fake'

# SendGrid
SENDGRID_API_KEY = 'SG.test-fake'

# FedEx
FEDEX_API_KEY = 'test-fedex-key'
FEDEX_API_SECRET = 'test-fedex-secret'
FEDEX_ACCOUNT_NUMBER = 'test-account'
FEDEX_AUTH_URL = "https://apis-sandbox.fedex.com/oauth/token"
FEDEX_SHIPMENT_URL = "https://apis-sandbox.fedex.com/ship/v1/shipments"

# GitHub webhook
GITHUB_WEBHOOK_SECRET = 'test-webhook-secret'

SHIPPING_COST = 5.00

SITE_ID = 1

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    }
}

# Disable security redirects for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Explorer permission
EXPLORER_PERMISSION_VIEW = lambda request: request.user.is_authenticated

# Password hashers - use fast hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
