import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from djangorestframework_camel_case.parser import CamelCaseMultiPartParser

from apps.clients.views import TenantAPIView
from apps.clients.models import ClientCompany
from apps.radar_documents.models import Document, DocumentType, DocumentRequest
from apps.radar_documents.serializers import DocumentSerializer, DocumentTypeSerializer, DocumentRequestSerializer
from apps.storage.services import StorageService

logger = logging.getLogger(__name__)


class DocumentListCreateView(TenantAPIView):
    parser_classes = [CamelCaseMultiPartParser, MultiPartParser, FormParser]

    def get(self, request):
        qs = Document.objects.filter(organization=request.tenant).select_related("client", "document_type")
        qp = request.query_params
        if qp.get("clientId"):
            qs = qs.filter(client_id=qp["clientId"])
        if qp.get("typeId"):
            qs = qs.filter(document_type_id=qp["typeId"])
        if qp.get("status"):
            qs = qs.filter(status=qp["status"])
        qs = qs.order_by("-created_at")
        data = DocumentSerializer(qs, many=True).data
        return Response({"documents": data, "total": len(data)})

    def post(self, request):
        client = get_object_or_404(ClientCompany, pk=request.data.get("client_id"), organization=request.tenant)
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "Arquivo obrigatorio."}, status=status.HTTP_400_BAD_REQUEST)

        type_id = request.data.get("type_id")
        doc_type = DocumentType.objects.filter(pk=type_id, organization=request.tenant).first() if type_id else None

        key = f"org-{request.tenant.id}/clients/{client.id}/documents/{file_obj.name}"
        stored = StorageService.upload_file(
            key=key, data=file_obj, content_type=file_obj.content_type,
            organization=request.tenant, uploaded_by=request.user,
        )

        task_id = request.data.get("task_id")

        document = Document.objects.create(
            organization=request.tenant,
            client=client,
            document_type=doc_type,
            name=request.data.get("name") or file_obj.name,
            status=Document.STATUS_RECEBIDO,
            notes=request.data.get("notes", ""),
            stored_object_id=stored["id"],
            task_id=task_id or None,
        )

        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)


class DocumentDetailView(TenantAPIView):
    def get_object(self, request, pk):
        return get_object_or_404(Document, pk=pk, organization=request.tenant)

    def get(self, request, pk):
        return Response(DocumentSerializer(self.get_object(request, pk)).data)

    def put(self, request, pk):
        document = self.get_object(request, pk)
        new_status = request.data.get("status")
        if new_status:
            document.status = new_status
            if new_status == Document.STATUS_REJEITADO:
                document.rejection_reason = request.data.get("rejection_reason", document.rejection_reason)
        for field in ("name", "validity_date", "notes", "competence"):
            if field in request.data:
                setattr(document, field, request.data[field])
        document.save()
        return Response(DocumentSerializer(document).data)

    def delete(self, request, pk):
        self.get_object(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentTypeListCreateView(TenantAPIView):
    def get(self, request):
        return Response(DocumentTypeSerializer(DocumentType.objects.filter(organization=request.tenant), many=True).data)

    def post(self, request):
        serializer = DocumentTypeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc_type = DocumentType.objects.create(organization=request.tenant, **serializer.validated_data)
        return Response(DocumentTypeSerializer(doc_type).data, status=status.HTTP_201_CREATED)


class DocumentTypeDetailView(TenantAPIView):
    def put(self, request, pk):
        doc_type = get_object_or_404(DocumentType, pk=pk, organization=request.tenant)
        serializer = DocumentTypeSerializer(doc_type, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        doc_type = get_object_or_404(DocumentType, pk=pk, organization=request.tenant)
        doc_type.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentRequestListCreateView(TenantAPIView):
    def get(self, request):
        qs = DocumentRequest.objects.filter(organization=request.tenant)
        qp = request.query_params
        if qp.get("clientId"):
            qs = qs.filter(client_id=qp["clientId"])
        if qp.get("status"):
            qs = qs.filter(status=qp["status"])
        data = DocumentRequestSerializer(qs.order_by("-created_at"), many=True).data
        return Response({"requests": data})

    def post(self, request):
        client = get_object_or_404(ClientCompany, pk=request.data.get("client_id"), organization=request.tenant)
        serializer = DocumentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = {k: v for k, v in serializer.validated_data.items() if k != "client_id"}
        doc_request = DocumentRequest.objects.create(
            organization=request.tenant, client=client, requested_by=request.user, **validated,
        )
        return Response(DocumentRequestSerializer(doc_request).data, status=status.HTTP_201_CREATED)
