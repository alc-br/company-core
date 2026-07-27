"""Root URL configuration for Company Core."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

URL_PREFIX = getattr(settings, "URL_PREFIX", "")

urlpatterns = [
    path(f"{URL_PREFIX}admin/", admin.site.urls),
    # Health checks
    path(f"{URL_PREFIX}health/", include("apps.health.urls")),
    # Celery progress
    path(f"{URL_PREFIX}celery-progress/", include("celery_progress.urls")),
    # API
    path(f"{URL_PREFIX}api/v1/", include("apps.api.v1.urls")),
    # Auth (allauth)
    path(f"{URL_PREFIX}account/", include("allauth.urls")),
]

if settings.DEBUG:
    # Django Debug Toolbar
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    # Static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
