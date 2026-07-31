import csv
import logging

from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.models import ClientCompany, ClientContact, Tag, Department
from apps.clients.serializers import (
    ClientCompanyListSerializer,
    ClientCompanyDetailSerializer,
    ClientCompanyWriteSerializer,
    ClientContactSerializer,
    TagSerializer,
    DepartmentSerializer,
)
from apps.clients.selectors import get_client_queryset

logger = logging.getLogger(__name__)


class TenantAPIView(APIView):
    """Base view that requires an active tenant (organization)."""

    permission_classes = [IsAuthenticated]
    versioning_class = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not getattr(request, "tenant", None):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Nenhuma organização ativa para este usuário.")


class ClientListCreateView(TenantAPIView):
    def get(self, request):
        qs = get_client_queryset(
            organization=request.tenant,
            search=request.query_params.get("search"),
            status_filter=request.query_params.get("status"),
            segment=request.query_params.get("segment"),
            responsible_id=request.query_params.get("responsibleId"),
            tag_id=request.query_params.get("tagId"),
        )

        if request.query_params.get("export") == "csv":
            return self._export_csv(qs)

        total = qs.count()
        limit = int(request.query_params.get("limit", 25) or 25)
        page = int(request.query_params.get("page", 1) or 1)
        offset = (page - 1) * limit
        page_qs = qs[offset: offset + limit] if limit else qs

        data = ClientCompanyListSerializer(page_qs, many=True).data
        return Response({"clients": data, "total": total})

    def post(self, request):
        serializer = ClientCompanyWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.save(organization=request.tenant)
        return Response(ClientCompanyDetailSerializer(client).data, status=status.HTTP_201_CREATED)

    def _export_csv(self, qs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="clientes.csv"'
        writer = csv.writer(response)
        writer.writerow(["Nome", "Nome Fantasia", "CNPJ", "Regime", "Status", "Segmento"])
        for c in qs:
            writer.writerow([c.name, c.trade_name, c.cnpj, c.tax_regime, c.status, c.segment])
        return response


class ClientDetailView(TenantAPIView):
    def get_object(self, request, pk):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(ClientCompany, pk=pk, organization=request.tenant, is_deleted=False)

    def get(self, request, pk):
        client = self.get_object(request, pk)
        return Response(ClientCompanyDetailSerializer(client).data)

    def put(self, request, pk):
        client = self.get_object(request, pk)
        serializer = ClientCompanyWriteSerializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        client = serializer.save()
        return Response(ClientCompanyDetailSerializer(client).data)


class ClientContactListCreateView(TenantAPIView):
    def get(self, request, client_id):
        from django.shortcuts import get_object_or_404
        client = get_object_or_404(ClientCompany, pk=client_id, organization=request.tenant)
        return Response(ClientContactSerializer(client.contacts.all(), many=True).data)

    def post(self, request, client_id):
        from django.shortcuts import get_object_or_404
        client = get_object_or_404(ClientCompany, pk=client_id, organization=request.tenant)
        serializer = ClientContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = ClientContact.objects.create(organization=request.tenant, client=client, **serializer.validated_data)
        return Response(ClientContactSerializer(contact).data, status=status.HTTP_201_CREATED)


class ClientContactDetailView(TenantAPIView):
    def get_object(self, request, pk):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(ClientContact, pk=pk, organization=request.tenant)

    def put(self, request, pk):
        contact = self.get_object(request, pk)
        serializer = ClientContactSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagListCreateView(TenantAPIView):
    def get(self, request):
        return Response(TagSerializer(Tag.objects.filter(organization=request.tenant), many=True).data)

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag = Tag.objects.create(organization=request.tenant, **serializer.validated_data)
        return Response(TagSerializer(tag).data, status=status.HTTP_201_CREATED)


class DepartmentListCreateView(TenantAPIView):
    def get(self, request):
        return Response(DepartmentSerializer(Department.objects.filter(organization=request.tenant), many=True).data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dept = Department.objects.create(organization=request.tenant, **serializer.validated_data)
        return Response(DepartmentSerializer(dept).data, status=status.HTTP_201_CREATED)


class DepartmentDetailView(TenantAPIView):
    def put(self, request, pk):
        from django.shortcuts import get_object_or_404
        dept = get_object_or_404(Department, pk=pk, organization=request.tenant)
        serializer = DepartmentSerializer(dept, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
