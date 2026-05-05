"""
Django settings for TechShop e-commerce project.
Connects to Supabase PostgreSQL as the primary database.
All secrets are read from environment variables via python-decouple.
"""

from pathlib import Path
from decouple import config, Csv

# ---------------------------------------------------------------------------
# Base directory
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECRET_KEY = config('SECRET_KEY')

DEBUG_STR = config('DEBUG', default='True')
DEBUG = DEBUG_STR.lower() in ('true', '1', 'yes', 'on') if isinstance(DEBUG_STR, str) else bool(DEBUG_STR)

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = config(
        'ALLOWED_HOSTS',
        default='127.0.0.1,localhost',
        cast=Csv()
    )

# ---------------------------------------------------------------------------
# Stripe Payment Settings
# ---------------------------------------------------------------------------
STRIPE_PUBLIC_KEY  = config('STRIPE_PUBLIC_KEY',  default='')
STRIPE_SECRET_KEY  = config('STRIPE_SECRET_KEY',  default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# ---------------------------------------------------------------------------
# Supabase Settings  (for Auth / Storage / real-time features)
# ---------------------------------------------------------------------------
SUPABASE_URL              = config('SUPABASE_URL',              default='')
SUPABASE_ANON_KEY         = config('SUPABASE_ANON_KEY',         default='')
# WARNING: service_role key has admin DB access — never expose to the client.
SUPABASE_SERVICE_ROLE_KEY = config('SUPABASE_SERVICE_ROLE_KEY', default='')

# ---------------------------------------------------------------------------
# Installed Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # TechShop apps
    'store',
    'cart',
    'orders',
    'wishlist',
    'admin_dashboard',
    'templatetags',
    'invoices',
]

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',           # serve static files
    'techshop_proj.security.SecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'techshop_proj.urls'

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_context',
                'cart.context_processors.categories_context',
                'cart.context_processors.currency_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'techshop_proj.wsgi.application'

# ---------------------------------------------------------------------------
# Database — Supabase PostgreSQL
# Connection pooling is handled by psycopg2 via CONN_MAX_AGE.
# Use a connection pooler URL (port 6543) in production for Supabase pooling.
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     config('DB_NAME',     default='postgres'),
        'USER':     config('DB_USER',     default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST':     config('DB_HOST',     default='db.tduqzoqizziuacoyyfge.supabase.co'),
        'PORT':     config('DB_PORT',     default='5432'),
        'CONN_MAX_AGE': 60,   # Keep DB connections alive for 60 seconds (connection pooling)
        'OPTIONS': {
            'sslmode': 'require',   # Supabase requires SSL
            'connect_timeout': 10,
        },
    }
}

# ---------------------------------------------------------------------------
# Caching  — use per-site in-memory cache for product listings etc.
# Switch to Redis in production:
#   CACHE_URL = redis://:<password>@<host>:<port>/1
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'techshop-cache',
    }
}
CACHE_MIDDLEWARE_SECONDS = 300   # 5 min default cache
PRODUCT_CACHE_TTL = 300          # seconds to cache product listings

# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_HTTPONLY  = True
SESSION_COOKIE_SAMESITE  = 'Lax'
SESSION_COOKIE_SECURE    = not DEBUG   # HTTPS only in production

# ---------------------------------------------------------------------------
# Password Validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ---------------------------------------------------------------------------
# Static & Media Files
# ---------------------------------------------------------------------------
STATIC_URL  = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR.parent / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---------------------------------------------------------------------------
# Auth Redirects
# ---------------------------------------------------------------------------
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL           = '/accounts/login/'

# ---------------------------------------------------------------------------
# Default Primary Key
# ---------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Security Headers (production only)
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_HSTS_SECONDS            = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD            = True
    SECURE_SSL_REDIRECT            = True
    CSRF_COOKIE_SECURE             = True

# ---------------------------------------------------------------------------
# Logging  — errors go to console; easy to redirect to a file / Sentry
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',   # set to DEBUG to see all SQL queries
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------------------
# Allow a local_settings.py override for developer-specific tweaks
# (this file must be in .gitignore — it is)
# ---------------------------------------------------------------------------
try:
    from .local_settings import *  # noqa: F401,F403
except ImportError:
    pass
