from django.contrib import admin
from apps.webhooks.models import WebhookEndpoint, WebhookDelivery


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ("url", "organization", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("url", "organization__name")


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "event_type", "status", "attempts", "response_code", "created_at")
    list_filter = ("status", "event_type")
    date_hierarchy = "created_at"
