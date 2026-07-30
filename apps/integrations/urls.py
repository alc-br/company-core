"""URL configuration for integrations app."""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.integrations.views import (
    list_integrations,
    create_integration,
    edit_integration,
    delete_integration,
    IntegrationViewSet,
    IntegrationLogViewSet,
)

app_name = "integrations"

# Template URLs
urlpatterns = [
    path('', list_integrations, name='list'),
    path('create/', create_integration, name='create'),
    path('<int:pk>/edit/', edit_integration, name='edit'),
    path('<int:pk>/delete/', delete_integration, name='delete'),
]

# DRF API router URLs
router = DefaultRouter()
router.register(r'api/integrations', IntegrationViewSet, basename='api-integration')
router.register(r'api/logs', IntegrationLogViewSet, basename='api-integration-log')

urlpatterns += router.urls
