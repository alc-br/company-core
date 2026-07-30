"""URL configuration for notifications app."""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.notifications.views import (
    list_templates,
    list_channels,
    create_template,
    edit_template,
    delete_template,
    create_channel,
    edit_channel,
    delete_channel,
    NotificationChannelViewSet,
    NotificationTemplateViewSet,
    NotificationLogViewSet,
)

app_name = "notifications"

# Template URLs
urlpatterns = [
    path('', list_templates, name='list_templates'),
    path('channels/', list_channels, name='list_channels'),
    path('templates/create/', create_template, name='create_template'),
    path('templates/<int:pk>/edit/', edit_template, name='edit_template'),
    path('templates/<int:pk>/delete/', delete_template, name='delete_template'),
    path('channels/create/', create_channel, name='create_channel'),
    path('channels/<int:pk>/edit/', edit_channel, name='edit_channel'),
    path('channels/<int:pk>/delete/', delete_channel, name='delete_channel'),
]

# DRF API router URLs
router = DefaultRouter()
router.register(r'api/channels', NotificationChannelViewSet, basename='api-notification-channel')
router.register(r'api/templates', NotificationTemplateViewSet, basename='api-notification-template')
router.register(r'api/logs', NotificationLogViewSet, basename='api-notification-log')

urlpatterns += router.urls
