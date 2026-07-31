from django.contrib import admin
from apps.radar_templates.models import Template, TemplateVersion, TemplateApplication


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "status", "current_version", "category"]
    list_filter = ["status", "organization"]
    search_fields = ["name", "code"]


@admin.register(TemplateVersion)
class TemplateVersionAdmin(admin.ModelAdmin):
    list_display = ["template", "version_number", "is_current", "published_at"]


@admin.register(TemplateApplication)
class TemplateApplicationAdmin(admin.ModelAdmin):
    list_display = ["template", "client", "template_version", "status", "base_date"]
    list_filter = ["status"]
