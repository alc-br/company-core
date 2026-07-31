from rest_framework import serializers
from apps.api.serializers import NullToBlankMixin
from apps.clients.models import ClientCompany, ClientContact, Tag, Department


class TagSerializer(NullToBlankMixin, serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color"]


class DepartmentSerializer(NullToBlankMixin, serializers.ModelSerializer):
    NULLABLE_FIELDS = {"manager"}

    class Meta:
        model = Department
        fields = ["id", "name", "description", "color", "manager"]


class ClientContactSerializer(NullToBlankMixin, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    NULLABLE_FIELDS = {"password"}

    class Meta:
        model = ClientContact
        fields = ["id", "name", "email", "phone", "role", "has_portal_access", "notes", "password", "created_at"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        contact = super().create(validated_data)
        if password:
            self._set_password(contact, password)
        return contact

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        contact = super().update(instance, validated_data)
        if password:
            self._set_password(contact, password)
        return contact

    @staticmethod
    def _set_password(contact, password):
        from django.contrib.auth.hashers import make_password
        contact.password_hash = make_password(password)
        contact.save(update_fields=["password_hash"])


class ClientCompanyListSerializer(serializers.ModelSerializer):
    tags_list = TagSerializer(source="tags", many=True, read_only=True)
    pending_tasks = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    applications = serializers.SerializerMethodField()

    class Meta:
        model = ClientCompany
        fields = [
            "id", "name", "trade_name", "cnpj", "tax_regime", "status",
            "responsible", "segment", "tags_list", "pending_tasks", "count",
            "applications", "created_at", "updated_at",
        ]

    def get_pending_tasks(self, obj):
        return getattr(obj, "pending_tasks_count", 0)

    def get_count(self, obj):
        return {
            "tasks": getattr(obj, "tasks_count", 0),
            "documents": getattr(obj, "documents_count", 0),
            "contacts": obj.contacts.count(),
        }

    def get_applications(self, obj):
        try:
            from apps.radar_templates.serializers import TemplateApplicationMiniSerializer
            return TemplateApplicationMiniSerializer(obj.template_applications.all()[:20], many=True).data
        except (ImportError, AttributeError):
            return []


class ClientCompanyDetailSerializer(ClientCompanyListSerializer):
    contacts = ClientContactSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    overdue_tasks_count = serializers.SerializerMethodField()
    active_applications_count = serializers.SerializerMethodField()
    next_due_date = serializers.SerializerMethodField()

    class Meta(ClientCompanyListSerializer.Meta):
        fields = ClientCompanyListSerializer.Meta.fields + [
            "ie", "im", "cnae", "company_size", "open_date", "email", "phone",
            "address", "city", "state", "zip_code", "notes", "portal_access",
            "service_start_date", "contacts", "tasks", "documents",
            "overdue_tasks_count", "active_applications_count", "next_due_date",
        ]

    def get_tasks(self, obj):
        try:
            from apps.radar_tasks.serializers import TaskMiniSerializer
            return TaskMiniSerializer(obj.radar_tasks.exclude(status="cancelada")[:50], many=True).data
        except (ImportError, AttributeError):
            return []

    def get_documents(self, obj):
        try:
            from apps.radar_documents.serializers import DocumentMiniSerializer
            return DocumentMiniSerializer(obj.documents.all()[:50], many=True).data
        except (ImportError, AttributeError):
            return []

    def get_overdue_tasks_count(self, obj):
        try:
            from django.utils import timezone
            return obj.radar_tasks.filter(status__in=["a_fazer", "em_andamento"], due_date__lt=timezone.now()).count()
        except (ImportError, AttributeError):
            return 0

    def get_active_applications_count(self, obj):
        try:
            return obj.template_applications.filter(status="active").count()
        except (ImportError, AttributeError):
            return 0

    def get_next_due_date(self, obj):
        try:
            from django.utils import timezone
            task = (
                obj.radar_tasks.filter(status__in=["a_fazer", "em_andamento"], due_date__gte=timezone.now())
                .order_by("due_date")
                .first()
            )
            return task.due_date if task else None
        except (ImportError, AttributeError):
            return None


class ClientCompanyWriteSerializer(NullToBlankMixin, serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    add_tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False, write_only=True)

    NULLABLE_FIELDS = {"open_date", "service_start_date", "responsible", "tags", "add_tags"}

    class Meta:
        model = ClientCompany
        fields = [
            "name", "trade_name", "cnpj", "ie", "im", "cnae", "tax_regime",
            "company_size", "segment", "open_date", "status", "responsible",
            "email", "phone", "address", "city", "state", "zip_code", "notes",
            "portal_access", "service_start_date", "tags", "add_tags",
        ]
        extra_kwargs = {field: {"required": False} for field in fields}

    def update(self, instance, validated_data):
        add_tags = validated_data.pop("add_tags", None)
        instance = super().update(instance, validated_data)
        if add_tags:
            instance.tags.add(*add_tags)
        return instance
