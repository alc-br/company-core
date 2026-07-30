from django.apps import AppConfig


class AiAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.ai"
    verbose_name = "AI"

    def ready(self):
        import apps.ai.signals  # noqa: F401
