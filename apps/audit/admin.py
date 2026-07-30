from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "target_type", "target_id", "organization", "created_at")
    list_filter = ("action", "target_type")
    search_fields = ("actor__email", "action", "target_type")
    readonly_fields = ("actor", "action", "target_type", "target_id", "ip_address", "user_agent", "created_at", "updated_at")
    date_hierarchy = "created_at"
