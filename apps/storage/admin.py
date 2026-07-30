from django.contrib import admin
from apps.storage.models import StorageBackendConfig, StoredObject


@admin.register(StorageBackendConfig)
class StorageBackendConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "backend_type", "is_default", "organization")
    list_filter = ("backend_type", "is_default")


@admin.register(StoredObject)
class StoredObjectAdmin(admin.ModelAdmin):
    list_display = ("key", "bucket", "size", "content_type", "organization", "created_at")
    list_filter = ("content_type",)
    search_fields = ("key", "organization__name")
