from django.contrib import admin
from apps.clients.models import ClientCompany, ClientContact, Tag, Department


@admin.register(ClientCompany)
class ClientCompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "trade_name", "cnpj", "organization", "status", "responsible", "created_at"]
    list_filter = ["status", "organization"]
    search_fields = ["name", "trade_name", "cnpj"]


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    list_display = ["name", "client", "email", "has_portal_access"]
    search_fields = ["name", "email"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "color"]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "manager"]
