from django.contrib import admin
from apps.integrations.models import Integration, IntegrationLog


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ("name", "integration_type", "organization", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "organization__name")


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ("integration", "action", "status", "duration_ms", "created_at")
    list_filter = ("status",)
    date_hierarchy = "created_at"
