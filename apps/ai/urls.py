"""URL configuration for AI app."""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.ai.views import (
    list_providers,
    create_provider,
    edit_provider,
    delete_provider,
    AIProviderConfigViewSet,
    AIModelConfigViewSet,
    AICallLogViewSet,
)

app_name = "ai"

# Template URLs
urlpatterns = [
    path('', list_providers, name='list'),
    path('create/', create_provider, name='create'),
    path('<int:pk>/edit/', edit_provider, name='edit'),
    path('<int:pk>/delete/', delete_provider, name='delete'),
]

# DRF API router URLs
router = DefaultRouter()
router.register(r'api/providers', AIProviderConfigViewSet, basename='api-ai-provider')
router.register(r'api/models', AIModelConfigViewSet, basename='api-ai-model-config')
router.register(r'api/call-logs', AICallLogViewSet, basename='api-ai-call-log')

urlpatterns += router.urls
