from django.contrib import admin
from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(FeatureFlagAssignment)
class FeatureFlagAssignmentAdmin(admin.ModelAdmin):
    list_display = ("flag", "organization", "user", "environment", "is_active")
    list_filter = ("is_active", "environment")
