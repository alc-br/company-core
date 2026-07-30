from django.contrib import admin
from apps.quotas.models import QuotaDefinition, QuotaAllocation


@admin.register(QuotaDefinition)
class QuotaDefinitionAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "unit", "default_limit")
    search_fields = ("code", "name")


@admin.register(QuotaAllocation)
class QuotaAllocationAdmin(admin.ModelAdmin):
    list_display = ("organization", "definition", "used", "limit", "period_start", "period_end")
    list_filter = ("definition",)
    search_fields = ("organization__name",)
