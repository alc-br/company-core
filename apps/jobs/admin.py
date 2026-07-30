from django.contrib import admin
from apps.jobs.models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("name", "task_path", "status", "priority", "retries", "scheduled_at", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("name", "task_path")
    date_hierarchy = "created_at"
