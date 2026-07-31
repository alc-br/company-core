from rest_framework import serializers
from apps.radar_templates.models import Template, TemplateVersion, TemplateApplication


def _stages_count(stages):
    return len(stages or [])


def _tasks_count(stages):
    return sum(len(stage.get("tasks", []) or []) for stage in (stages or []))


class TemplateApplicationMiniSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    template = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()

    class Meta:
        model = TemplateApplication
        fields = ["id", "base_date", "status", "created_at", "template", "version"]

    def get_template(self, obj):
        return {"id": obj.template_id, "name": obj.template.name}

    def get_version(self, obj):
        return {"versionNumber": obj.template_version.version_number}


class TemplateApplicationClientMiniSerializer(serializers.Serializer):
    """Aplicacao vista do lado do template (lista clientes que usam cada versao)."""
    id = serializers.IntegerField()
    base_date = serializers.DateField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["client"] = {"id": instance.client_id, "name": instance.client.name, "cnpj": instance.client.cnpj}
        data["version"] = {"versionNumber": instance.template_version.version_number}
        return data


class TemplateListSerializer(serializers.ModelSerializer):
    responsible_name = serializers.SerializerMethodField()
    stages_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = [
            "id", "name", "code", "description", "category", "color", "status",
            "current_version", "responsible_name", "stages_count", "tasks_count",
            "count", "department", "created_at", "updated_at",
        ]

    def get_responsible_name(self, obj):
        return obj.responsible.get_display_name() if obj.responsible_id else None

    def get_stages_count(self, obj):
        return _stages_count(obj.stages)

    def get_tasks_count(self, obj):
        return _tasks_count(obj.stages)

    def get_count(self, obj):
        return {"versions": obj.versions.count(), "applications": obj.applications.count()}

    def get_department(self, obj):
        if not obj.department_id:
            return None
        return {"id": obj.department_id, "name": obj.department.name}


class TemplateDetailSerializer(TemplateListSerializer):
    responsible_id = serializers.IntegerField(source="responsible.id", read_only=True, default=None)
    applications = serializers.SerializerMethodField()

    class Meta(TemplateListSerializer.Meta):
        fields = TemplateListSerializer.Meta.fields + [
            "purpose", "responsible_id", "instructions", "warning",
            "default_periodicity", "variables", "stages", "applications",
        ]

    def get_applications(self, obj):
        return TemplateApplicationClientMiniSerializer(
            obj.applications.select_related("client", "template_version")[:50], many=True
        ).data


class TemplateWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            "name", "code", "description", "purpose", "category", "color",
            "responsible", "department", "instructions", "warning",
            "default_periodicity", "variables", "stages", "status",
        ]
        extra_kwargs = {field: {"required": False} for field in fields}


class TemplateVersionSerializer(serializers.ModelSerializer):
    published_by_name = serializers.SerializerMethodField()
    is_current = serializers.BooleanField()
    is_draft = serializers.SerializerMethodField()
    stages_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = TemplateVersion
        fields = [
            "id", "version_number", "published_at", "published_by_name",
            "is_current", "is_draft", "stages_count", "tasks_count", "applications_count", "created_at",
        ]

    def get_published_by_name(self, obj):
        return obj.published_by.get_display_name() if obj.published_by_id else None

    def get_is_draft(self, obj):
        return False

    def get_stages_count(self, obj):
        return _stages_count(obj.stages_snapshot)

    def get_tasks_count(self, obj):
        return _tasks_count(obj.stages_snapshot)

    def get_applications_count(self, obj):
        return obj.applications.count()


class TemplateApplicationWriteSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    template_version_id = serializers.IntegerField(required=False)
    client_id = serializers.IntegerField()
    base_date = serializers.DateField()
    variables = serializers.JSONField(required=False, default=dict)
    role_mappings = serializers.JSONField(required=False, default=dict)
