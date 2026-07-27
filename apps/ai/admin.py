from django.contrib import admin
from apps.ai.models import AIProviderConfig, AIModelConfig, AICallLog


@admin.register(AIProviderConfig)
class AIProviderConfigAdmin(admin.ModelAdmin):
    list_display = ("display_name", "provider_name", "is_default", "created_at")
    search_fields = ("display_name",)
    list_filter = ("provider_name", "is_default")


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ("display_name", "model_id", "provider", "max_tokens", "created_at")
    search_fields = ("display_name", "model_id")
    list_filter = ("provider",)


@admin.register(AICallLog)
class AICallLogAdmin(admin.ModelAdmin):
    list_display = ("provider_name", "model", "tokens_input", "tokens_output", "cost", "created_at")
    search_fields = ("provider_name", "model")
    list_filter = ("provider_name",)
    readonly_fields = ("organization", "user", "provider_name", "model", "tokens_input", "tokens_output", "cost", "latency_ms", "metadata")
