from django.contrib import admin
from apps.analytics.models import AnalyticsEvent, AnalyticsAggregation


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "module", "organization", "user", "timestamp")
    list_filter = ("event_type", "module")
    search_fields = ("event_type", "organization__name")
    date_hierarchy = "timestamp"


@admin.register(AnalyticsAggregation)
class AnalyticsAggregationAdmin(admin.ModelAdmin):
    list_display = ("organization", "period", "module", "metric", "value")
    list_filter = ("module",)
