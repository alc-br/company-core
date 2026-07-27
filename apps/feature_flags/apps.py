from django.apps import AppConfig


class FeatureFlagsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.feature_flags"
    verbose_name = "Feature Flags"

    def ready(self):
        import apps.feature_flags.signals  # noqa: F401
