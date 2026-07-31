from django.contrib import admin
from apps.radar_reports.models import ExportJob


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ["type", "organization", "status", "requested_by", "created_at"]
    list_filter = ["status", "type"]
