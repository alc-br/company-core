from django.contrib import admin
from apps.radar_tasks.models import Task, ChecklistItem, TaskComment, TaskDependency, TaskFollower


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "organization", "client", "status", "priority", "due_date"]
    list_filter = ["status", "priority", "organization"]
    search_fields = ["title"]


admin.site.register(ChecklistItem)
admin.site.register(TaskComment)
admin.site.register(TaskDependency)
admin.site.register(TaskFollower)
