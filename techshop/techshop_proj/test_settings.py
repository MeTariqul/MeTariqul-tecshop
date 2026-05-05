"""
test_settings.py — Settings overrides used exclusively by pytest.

Inherits everything from the production settings, but replaces the
Supabase PostgreSQL database with a local SQLite database so that
the test suite can run offline without needing network access.

Selected by pytest via pytest.ini:
    DJANGO_SETTINGS_MODULE = techshop_proj.test_settings
"""

from .settings import *  # noqa: F401, F403 — import all production settings

# ---------------------------------------------------------------------------
# Override: use SQLite for tests (fast, offline, no Supabase connection needed)
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',  # noqa: F405 — BASE_DIR from settings
    }
}

# ---------------------------------------------------------------------------
# Speed up password hashing in tests (no security tradeoff — tests only)
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# ---------------------------------------------------------------------------
# Disable cache during tests to avoid stale data leaking between test runs
# ---------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# ---------------------------------------------------------------------------
# Silence storage deprecation warning — use STORAGES dict (Django 4.2+)
# STATICFILES_STORAGE and STORAGES are mutually exclusive; remove the
# inherited value from production settings before defining STORAGES.
# ---------------------------------------------------------------------------
STATICFILES_STORAGE = None   # clear the inherited value (Django ignores None)
globals().pop('STATICFILES_STORAGE', None)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# Make media uploads use a temp directory during tests
# ---------------------------------------------------------------------------
import tempfile  # noqa: E402
MEDIA_ROOT = tempfile.mkdtemp()

# ---------------------------------------------------------------------------
# Suppress security middleware HTTPS redirect during tests
# ---------------------------------------------------------------------------
MIDDLEWARE = [m for m in MIDDLEWARE if 'SecurityHeadersMiddleware' not in m]  # noqa: F405
