"""Test settings for Company Core."""

from company_core.settings.base import *  # noqa: F401, F403

DEBUG = False
SECRET_KEY = "test-secret-key-for-ci-only"
DATABASES["default"]["NAME"] = "test_company_core"
DATABASES["default"]["ENGINE"] = "django.db.backends.sqlite3"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+dummy://"
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
MEDIA_ROOT = BASE_DIR / "test_media"
STATIC_ROOT = BASE_DIR / "test_staticfiles"
