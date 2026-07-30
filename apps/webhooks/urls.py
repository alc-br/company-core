"""URL configuration for webhooks app."""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.webhooks.views import (
    list_endpoints,
    create_endpoint,
    edit_endpoint,
    delete_endpoint,
    test_endpoint,
    WebhookEndpointViewSet,
    WebhookDeliveryViewSet,
)

app_name = "webhooks"

# Template URLs
urlpatterns = [
    path('', list_endpoints, name='list'),
    path('create/', create_endpoint, name='create'),
    path('<int:pk>/edit/', edit_endpoint, name='edit'),
    path('<int:pk>/delete/', delete_endpoint, name='delete'),
    path('<int:pk>/test/', test_endpoint, name='test'),
]

# DRF API router URLs
router = DefaultRouter()
router.register(r'api/endpoints', WebhookEndpointViewSet, basename='api-webhook-endpoint')
router.register(r'api/deliveries', WebhookDeliveryViewSet, basename='api-webhook-delivery')

urlpatterns += router.urls
