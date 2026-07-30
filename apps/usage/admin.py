from django.contrib import admin
from apps.usage.models import UsageRecord


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "metric_type", "value", "period")
    list_filter = ("metric_type",)
    search_fields = ("organization__name",)
