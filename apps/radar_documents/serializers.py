from rest_framework import serializers
from apps.api.serializers import NullToBlankMixin
from apps.radar_documents.models import Document, DocumentType, DocumentRequest


class DocumentTypeSerializer(NullToBlankMixin, serializers.ModelSerializer):
    NULLABLE_FIELDS = {"validity_days"}

    class Meta:
        model = DocumentType
        fields = ["id", "name", "category", "allowed_formats", "max_size_mb", "validity_days"]


class DocumentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "name", "status", "competence", "created_at"]


class DocumentSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id", "name", "client_id", "status", "validity_date", "competence",
            "notes", "rejection_reason", "task_id", "request_id", "url",
            "client", "document_type", "created_at", "updated_at",
        ]

    def get_client(self, obj):
        return {"id": obj.client_id, "name": obj.client.name}

    def get_document_type(self, obj):
        if not obj.document_type_id:
            return None
        return {"id": obj.document_type_id, "name": obj.document_type.name}

    def get_url(self, obj):
        if not obj.stored_object_id:
            return None
        from django.conf import settings
        from django.core.files.storage import default_storage
        try:
            url = default_storage.url(obj.stored_object.key)
        except Exception:
            return None
        # a URL assinada aponta pro endpoint interno do MinIO (rede docker);
        # reescreve para o path publico /storage/ exposto pelo nginx.
        internal = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
        if internal and url.startswith(internal):
            request = self.context.get("request")
            base = request.build_absolute_uri("/storage/") if request else "/storage/"
            url = base.rstrip("/") + "/" + url[len(internal):].lstrip("/")
        return url


class DocumentRequestSerializer(NullToBlankMixin, serializers.ModelSerializer):
    NULLABLE_FIELDS = {"due_date"}

    class Meta:
        model = DocumentRequest
        fields = [
            "id", "title", "instructions", "due_date", "accepted_formats",
            "reminder_1d", "reminder_3d", "reminder_7d", "status", "client_id", "created_at",
        ]
