import json
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.clients.models import ClientCompany
from apps.radar_templates.models import Template, TemplateVersion, TemplateApplication
from apps.radar_templates.serializers import (
    TemplateListSerializer,
    TemplateDetailSerializer,
    TemplateWriteSerializer,
    TemplateVersionSerializer,
    TemplateApplicationWriteSerializer,
)

logger = logging.getLogger(__name__)


def _as_json(value, default):
    """O frontend as vezes manda listas/objetos JSON como string; aceita os dois formatos."""
    if isinstance(value, str):
        try:
            return json.loads(value) if value else default
        except json.JSONDecodeError:
            return default
    return value if value is not None else default


class TemplateListCreateView(TenantAPIView):
    def get(self, request):
        qs = Template.objects.filter(organization=request.tenant).select_related("responsible", "department")

        search = request.query_params.get("search")
        category = request.query_params.get("category")
        status_filter = request.query_params.get("status")
        author = request.query_params.get("author")

        if search:
            from django.db.models import Q
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category=category)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if author:
            qs = qs.filter(responsible_id=author)

        return Response(TemplateListSerializer(qs, many=True).data)

    def post(self, request):
        data = dict(request.data)
        data["variables"] = _as_json(data.get("variables"), [])
        data["stages"] = _as_json(data.get("stages"), [])

        serializer = TemplateWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        template = serializer.save(organization=request.tenant)
        return Response(TemplateDetailSerializer(template).data, status=status.HTTP_201_CREATED)


class TemplateDetailView(TenantAPIView):
    def get_object(self, request, pk):
        return get_object_or_404(Template, pk=pk, organization=request.tenant)

    def get(self, request, pk):
        return Response(TemplateDetailSerializer(self.get_object(request, pk)).data)

    def put(self, request, pk):
        template = self.get_object(request, pk)
        data = dict(request.data)
        if "variables" in data:
            data["variables"] = _as_json(data.get("variables"), [])
        if "stages" in data:
            data["stages"] = _as_json(data.get("stages"), [])

        serializer = TemplateWriteSerializer(template, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        template = serializer.save()
        return Response(TemplateDetailSerializer(template).data)

    def delete(self, request, pk):
        self.get_object(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TemplateVersionListView(TenantAPIView):
    def get(self, request, pk):
        template = get_object_or_404(Template, pk=pk, organization=request.tenant)
        versions = template.versions.all()
        return Response({"versions": TemplateVersionSerializer(versions, many=True).data})


class TemplatePublishView(TenantAPIView):
    @transaction.atomic
    def post(self, request, pk):
        template = get_object_or_404(Template.objects.select_for_update(), pk=pk, organization=request.tenant)

        errors = []
        warnings = []
        stages = template.stages or []
        if not stages:
            errors.append("O template precisa de ao menos uma etapa.")
        total_tasks = 0
        for stage in stages:
            if not (stage.get("name") or "").strip():
                errors.append("Existe uma etapa sem nome.")
            tasks = stage.get("tasks") or []
            total_tasks += len(tasks)
            for task in tasks:
                if not (task.get("title") or "").strip():
                    errors.append("Existe uma tarefa sem titulo.")
                if not task.get("department") and not task.get("role"):
                    warnings.append(f"Tarefa '{task.get('title', '?')}' sem departamento responsavel.")
        if total_tasks == 0:
            errors.append("O template precisa de ao menos uma tarefa.")

        if errors:
            return Response({"error": " ".join(errors), "errors": errors, "warnings": warnings}, status=status.HTTP_400_BAD_REQUEST)

        next_version = template.current_version + 1
        published_by_id = request.data.get("published_by") or request.user.id

        TemplateVersion.objects.filter(template=template, is_current=True).update(is_current=False)
        version = TemplateVersion.objects.create(
            organization=request.tenant,
            template=template,
            version_number=next_version,
            name=template.name,
            stages_snapshot=stages,
            metadata_snapshot={
                "description": template.description, "purpose": template.purpose,
                "category": template.category, "color": template.color,
                "instructions": template.instructions, "warning": template.warning,
                "defaultPeriodicity": template.default_periodicity, "variables": template.variables,
            },
            is_current=True,
            published_by_id=published_by_id,
        )
        template.current_version = next_version
        template.status = Template.STATUS_PUBLISHED
        template.save(update_fields=["current_version", "status", "updated_at"])

        return Response({"version": TemplateVersionSerializer(version).data, "warnings": warnings}, status=status.HTTP_201_CREATED)


class TemplateApplicationListCreateView(TenantAPIView):
    def post(self, request):
        serializer = TemplateApplicationWriteSerializer(data={
            **request.data,
            "variables": _as_json(request.data.get("variables"), {}),
            "role_mappings": _as_json(request.data.get("role_mappings"), {}),
        })
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        template = get_object_or_404(Template, pk=payload["template_id"], organization=request.tenant)
        client = get_object_or_404(ClientCompany, pk=payload["client_id"], organization=request.tenant)
        version_id = payload.get("template_version_id")
        version = (
            get_object_or_404(TemplateVersion, pk=version_id, template=template)
            if version_id else
            get_object_or_404(TemplateVersion, template=template, is_current=True)
        )

        application = TemplateApplication.objects.create(
            organization=request.tenant,
            template=template,
            template_version=version,
            client=client,
            base_date=payload["base_date"],
            variables=payload["variables"],
            role_mappings=payload["role_mappings"],
            applied_by=request.user,
        )

        try:
            from apps.radar_tasks.services import generate_tasks_from_application
            generate_tasks_from_application(application)
        except ImportError:
            logger.warning("apps.radar_tasks ainda nao disponivel; aplicacao criada sem gerar tarefas.")

        from apps.radar_templates.serializers import TemplateApplicationMiniSerializer
        return Response(TemplateApplicationMiniSerializer(application).data, status=status.HTTP_201_CREATED)
