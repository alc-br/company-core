import logging
from django.core.cache import cache
from apps.settings.models import TenantSetting, GlobalSetting


logger = logging.getLogger(__name__)


class SettingsService:
    """Service layer for settings operations."""

    CACHE_PREFIX = "tenant_settings"
    CACHE_TIMEOUT = 300

    @staticmethod
    def get(organization, key, default=None, environment="production"):
        """Get a tenant setting value (with caching)."""
        cache_key = f"{SettingsService.CACHE_PREFIX}:{organization.id}:{key}:{environment}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            setting = TenantSetting.objects.get(
                organization=organization, key=key, environment=environment
            )
            result = setting.value
        except TenantSetting.DoesNotExist:
            result = default
        cache.set(cache_key, result, SettingsService.CACHE_TIMEOUT)
        return result

    @staticmethod
    def set(organization, key, value, environment="production"):
        """Set a tenant setting value."""
        setting, created = TenantSetting.objects.update_or_create(
            organization=organization,
            key=key,
            environment=environment,
            defaults={"value": value},
        )
        cache_key = f"{SettingsService.CACHE_PREFIX}:{organization.id}:{key}:{environment}"
        cache.delete(cache_key)
        action = "created" if created else "updated"
        logger.info(f"Tenant setting '{key}' {action} for org {organization.id}")
        return setting

    @staticmethod
    def delete_tenant_setting(organization, key, environment="production"):
        """Delete a tenant setting."""
        try:
            setting = TenantSetting.objects.get(
                organization=organization, key=key, environment=environment,
            )
            setting.delete()
            cache_key = f"{SettingsService.CACHE_PREFIX}:{organization.id}:{key}:{environment}"
            cache.delete(cache_key)
            logger.info(f"Tenant setting '{key}' deleted for org {organization.id}")
            return True
        except TenantSetting.DoesNotExist:
            return False

    @staticmethod
    def get_global(key, default=None):
        """Get a global setting value."""
        try:
            setting = GlobalSetting.objects.get(key=key)
            return setting.value
        except GlobalSetting.DoesNotExist:
            return default

    @staticmethod
    def set_global(key, value, description=""):
        """Set a global setting value."""
        setting, created = GlobalSetting.objects.update_or_create(
            key=key,
            defaults={"value": value, "description": description},
        )
        action = "created" if created else "updated"
        logger.info(f"Global setting '{key}' {action}")
        return setting

    @staticmethod
    def delete_global_setting(key):
        """Delete a global setting."""
        deleted = GlobalSetting.objects.filter(key=key).delete()
        if deleted[0] > 0:
            logger.info(f"Global setting '{key}' deleted")
        return deleted[0] > 0
