from django.contrib import admin
from apps.agents.models import Agent, AgentTool, AgentExecution


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("name", "model_id", "is_active", "organization", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
    filter_horizontal = ("tools",)


@admin.register(AgentTool)
class AgentToolAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "handler_path")
    search_fields = ("name", "code")


@admin.register(AgentExecution)
class AgentExecutionAdmin(admin.ModelAdmin):
    list_display = ("agent", "status", "tokens_used", "duration_ms", "created_at")
    search_fields = ("agent__name",)
    list_filter = ("status",)
    readonly_fields = ("agent", "input_data", "output_data", "tokens_used", "duration_ms", "error_message")
