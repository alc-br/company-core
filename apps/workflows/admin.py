from django.contrib import admin
from apps.workflows.models import Workflow, WorkflowExecution, WorkflowStepLog


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "organization__name")


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    list_display = ("workflow", "status", "current_step", "started_at", "completed_at")
    list_filter = ("status",)
    date_hierarchy = "started_at"


@admin.register(WorkflowStepLog)
class WorkflowStepLogAdmin(admin.ModelAdmin):
    list_display = ("execution", "step_name", "status", "duration_ms", "created_at")
    list_filter = ("status",)
