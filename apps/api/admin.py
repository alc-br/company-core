from django.contrib import admin
from apps.api.models import APIKey, PersonalAccessToken, ServiceAccount


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "prefix", "user", "organization", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "user__email", "organization__name")


@admin.register(PersonalAccessToken)
class PersonalAccessTokenAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "expires_at")
    search_fields = ("name", "user__email")


@admin.register(ServiceAccount)
class ServiceAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "organization__name")
