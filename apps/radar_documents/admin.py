from django.contrib import admin
from apps.radar_documents.models import Document, DocumentType, DocumentRequest

admin.site.register(DocumentType)
admin.site.register(DocumentRequest)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "client", "status", "document_type", "created_at"]
    list_filter = ["status", "organization"]
