"""Root URL configuration for Company Core."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

URL_PREFIX = getattr(settings, "URL_PREFIX", "")

urlpatterns = [
    path(f"{URL_PREFIX}", include("apps.web.urls")),
    path(f"{URL_PREFIX}admin/", admin.site.urls),
    # Health checks
    path(f"{URL_PREFIX}health/", include("apps.health.urls")),
    # Celery progress
    path(f"{URL_PREFIX}celery-progress/", include("celery_progress.urls")),
    # API
    path(f"{URL_PREFIX}api/v1/", include("apps.api.v1.urls")),
    # Auth JSON API (consumido pelo proxy do frontend Next.js)
    path(f"{URL_PREFIX}", include("apps.users.auth_urls")),
    # Auth (allauth, views HTML classicas)
    path(f"{URL_PREFIX}account/", include("allauth.urls")),
    # Modules
    path(f"{URL_PREFIX}orgs/", include("apps.organizations.urls")),
    path(f"{URL_PREFIX}billing/", include("apps.billing.urls")),
    path(f"{URL_PREFIX}ai/", include("apps.ai.urls")),
    path(f"{URL_PREFIX}agents/", include("apps.agents.urls")),
    path(f"{URL_PREFIX}audit/", include("apps.audit.urls")),
    path(f"{URL_PREFIX}permissions/", include("apps.permissions.urls")),
    path(f"{URL_PREFIX}quotas/", include("apps.quotas.urls")),
    path(f"{URL_PREFIX}flags/", include("apps.feature_flags.urls")),
    path(f"{URL_PREFIX}notifications/", include("apps.notifications.urls")),
    path(f"{URL_PREFIX}settings/", include("apps.settings.urls")),
    path(f"{URL_PREFIX}webhooks/", include("apps.webhooks.urls")),
    path(f"{URL_PREFIX}workflows/", include("apps.workflows.urls")),
    path(f"{URL_PREFIX}jobs/", include("apps.jobs.urls")),
    path(f"{URL_PREFIX}storage/", include("apps.storage.urls")),
    path(f"{URL_PREFIX}users/", include("apps.users.urls")),
    path(f"{URL_PREFIX}integrations/", include("apps.integrations.urls")),
    path(f"{URL_PREFIX}analytics/", include("apps.analytics.urls")),
    path(f"{URL_PREFIX}search/", include("apps.search.urls")),
    path(f"{URL_PREFIX}usage/", include("apps.usage.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
