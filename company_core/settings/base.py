"""
Base settings for Company Core project.
Built on top of SaaS Pegasus patterns.
"""

import os
import environ
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# ─── Environment ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
env.read_env(os.path.join(BASE_DIR, ".env"))

# ─── Core Django ───────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY", default="django-insecure-company-core-dev-key")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
ROOT_URLCONF = "company_core.urls"
WSGI_APPLICATION = "company_core.wsgi.application"
ASGI_APPLICATION = "company_core.asgi.application"

# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Site ──────────────────────────────────────────────────────
SITE_ID = 1
SITE_NAME = "Company Core"

# ─── Installed Apps ────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    # Authentication (Pegasus)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "corsheaders",
    # REST API
    "rest_framework",
    "drf_spectacular",
    # Celery
    "django_celery_beat",
    "django_celery_results",
    "celery_progress",
    # Feature Flags
    "waffle",
    # Storage
    "storages",
    # Health Checks (custom views in apps.health instead of django-health-check)
]

# Company Core Apps (registered in dependency order)
COMPANY_CORE_APPS = [
    "apps.users",
    "apps.common",
    "apps.core",
    "apps.settings",
    "apps.organizations",
    "apps.permissions",
    "apps.billing",
    "apps.quotas",
    "apps.feature_flags",
    "apps.ai",
    "apps.agents",
    "apps.notifications",
    "apps.integrations",
    "apps.audit",
    "apps.analytics",
    "apps.usage",
    "apps.storage",
    "apps.api",
    "apps.webhooks",
    "apps.workflows",
    "apps.jobs",
    "apps.sdk",
    "apps.health",
    "apps.search",
    "apps.admin_ext",
    "apps.web",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + COMPANY_CORE_APPS

# ─── Middleware ────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
    "apps.organizations.middleware.TenantMiddleware",
]

# ─── Database ─────────────────────────────────────────────────
# Support for file:// (SQLite), postgres://, postgresql:// URLs
_DATABASE_URL = env("DATABASE_URL", default=None)

if _DATABASE_URL and _DATABASE_URL.startswith(("postgres://", "postgresql://")):
    DATABASES = {"default": env.db_url("DATABASE_URL")}
elif _DATABASE_URL and _DATABASE_URL.startswith("file://"):
    import urllib.parse
    _parsed = urllib.parse.urlparse(_DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": _parsed.path or BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Default to SQLite for development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ─── Cache ────────────────────────────────────────────────────
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
        "KEY_PREFIX": "cc",
        "TIMEOUT": env.int("CACHE_TIMEOUT", default=300),
    }
}

if DEBUG:
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }

# ─── URLs ────────────────────────────────────────────────────
URL_PREFIX = ""

# ─── Templates ────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "company_core.context_processors.project_meta",
                "company_core.context_processors.csrf_settings",
            ],
        },
    },
]

# ─── Static Files ─────────────────────────────────────────────
STATIC_URL = f"{URL_PREFIX}/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# ─── Media Files ──────────────────────────────────────────────
MEDIA_URL = f"{URL_PREFIX}/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ─── Auth ─────────────────────────────────────────────────────
AUTH_USER_MODEL = "users.CustomUser"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ─── allauth ──────────────────────────────────────────────────
ACCOUNT_ADAPTER = "apps.users.adapter.EmailAsUsernameAdapter"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = env("ACCOUNT_EMAIL_VERIFICATION", default="none")
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Company Core] "

LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/account/login/"
LOGOUT_REDIRECT_URL = "/"

# ─── REST Framework ──────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.api.authentication.CsrfExemptSessionAuthentication",
        "apps.api.authentication.APIKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "apps.api.pagination.StandardizedPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_THROTTLE_CLASSES": [
        "apps.api.throttling.TenantRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/hour",
        "anon": "100/hour",
    },
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    "EXCEPTION_HANDLER": "apps.api.exception_handler.standard_exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# ─── drf-spectacular (OpenAPI) ────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Company Core API",
    "DESCRIPTION": "API REST da plataforma Company Core",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"apiKeyAuth": []}],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "apiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "API Key authentication (Bearer <key>)",
            }
        }
    },
}

# ─── Celery ──────────────────────────────────────────────────
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=env("REDIS_URL", default="redis://localhost:6379/0"))
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_RESULT_EXTENDED = True
CELERY_TRACK_STARTED = True
CELERY_TASK_ALWAYS_EAGER = DEBUG

# Celery Queues
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_QUEUES = {
    "default": {},
    "billing": {"routing_key": "billing"},
    "ai": {"routing_key": "ai"},
    "webhooks": {"routing_key": "webhooks"},
    "workflows": {"routing_key": "workflows"},
    "analytics": {"routing_key": "analytics"},
    "notifications": {"routing_key": "notifications"},
}
CELERY_TASK_ROUTES = {
    "apps.billing.tasks.*": {"queue": "billing"},
    "apps.ai.tasks.*": {"queue": "ai"},
    "apps.webhooks.tasks.*": {"queue": "webhooks"},
    "apps.workflows.tasks.*": {"queue": "workflows"},
    "apps.analytics.tasks.*": {"queue": "analytics"},
    "apps.notifications.tasks.*": {"queue": "notifications"},
}

# ─── Waffle (Feature Flags) ──────────────────────────────────
# We use django-waffle's built-in Flag model for template tags ({% flag %}).
# Our custom FeatureFlag model in apps.feature_flags provides per-org/user assignment.
WAFFLE_OVERRIDE = env.bool("WAFFLE_OVERRIDE", default=True)

# ─── Storage (S3 Compatible) ─────────────────────────────────
STORAGE_BACKEND = env("STORAGE_BACKEND", default="local")  # "s3", "minio", "r2", "local"

if STORAGE_BACKEND in ("s3", "minio", "r2"):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="company-core")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default=None)
    AWS_DEFAULT_ACL = "private"
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True

# ─── Email ─────────────────────────────────────────────────────
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@companycore.dev")

# ─── CORS ──────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=DEBUG)

# ─── i18n ─────────────────────────────────────────────────────
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ─── Logging ───────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if not DEBUG else "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ─── Celery Progress ───────────────────────────────────────────
CELERY_PROGRESS_TRACKER_URL = f"{URL_PREFIX}/celery-progress/"

# ─── Project Metadata ─────────────────────────────────────────
PROJECT_METADATA = {
    "NAME": _("Company Core"),
    "URL": env("PROJECT_URL", default="http://localhost:8000"),
    "DESCRIPTION": _("Plataforma SaaS multi-tenant"),
    "CONTACT_EMAIL": env("CONTACT_EMAIL", default="team@companycore.dev"),
}

# ─── Schedules (Celery Beat) ──────────────────────────────────
SCHEDULED_TASKS: dict = {}
