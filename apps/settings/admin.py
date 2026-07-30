from django.contrib import admin
from apps.settings.models import TenantSetting, GlobalSetting


@admin.register(TenantSetting)
class TenantSettingAdmin(admin.ModelAdmin):
    list_display = ("organization", "key", "value", "environment")
    list_filter = ("environment",)
    search_fields = ("organization__name", "key")


@admin.register(GlobalSetting)
class GlobalSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    search_fields = ("key",)
