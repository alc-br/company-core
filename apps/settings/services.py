from django.core.cache import cache
from apps.settings.models import TenantSetting, GlobalSetting


class SettingsService:
    CACHE_PREFIX = "tenant_settings"
    CACHE_TIMEOUT = 300

    @staticmethod
    def get(organization, key, default=None):
        cache_key = f"{SettingsService.CACHE_PREFIX}:{organization.id}:{key}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            setting = TenantSetting.objects.get(organization=organization, key=key)
            result = setting.value
        except TenantSetting.DoesNotExist:
            result = default
        cache.set(cache_key, result, SettingsService.CACHE_TIMEOUT)
        return result

    @staticmethod
    def set(organization, key, value, environment="production"):
        TenantSetting.objects.update_or_create(
            organization=organization,
            key=key,
            environment=environment,
            defaults={"value": value},
        )
        cache_key = f"{SettingsService.CACHE_PREFIX}:{organization.id}:{key}"
        cache.delete(cache_key)
