from django.contrib import admin
from apps.notifications.models import NotificationChannel, NotificationTemplate, NotificationLog


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "organization", "is_active")
    list_filter = ("type", "is_active")


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "subject", "channel")
    search_fields = ("code", "subject")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("recipient", "template", "status", "sent_at")
    list_filter = ("status",)
    search_fields = ("recipient",)
    date_hierarchy = "created_at"
