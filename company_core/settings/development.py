"""Development settings for Company Core."""

from company_core.settings.base import *  # noqa: F401, F403

# ─── Development Overrides ────────────────────────────────────
DEBUG = True

# Enable Django Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]

# Show emails in console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Celery eager mode (run tasks synchronously)
CELERY_TASK_ALWAYS_EAGER = True

# Disable caching
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}

# Security (relaxed for dev)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
