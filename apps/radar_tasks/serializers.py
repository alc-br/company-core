from rest_framework import serializers
from apps.api.serializers import NullToBlankMixin
from apps.radar_tasks.models import Task, ChecklistItem, TaskComment, TaskDependency, TaskFollower


class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ["id", "text", "done", "required", "order"]


class TaskCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ["id", "content", "user_name", "created_at"]

    def get_user_name(self, obj):
        return obj.user_name or (obj.user.get_display_name() if obj.user_id else None)


class TaskDependencyMiniSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    depends_on_id = serializers.IntegerField(source="depends_on_id")
    blocking_type = serializers.CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["depends_on_task"] = {
            "id": instance.depends_on_id,
            "title": instance.depends_on.title,
            "status": instance.depends_on.status,
            "priority": instance.depends_on.priority,
            "client": {"name": instance.depends_on.client.name} if instance.depends_on.client_id else None,
        }
        return data


class TaskFollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskFollower
        fields = ["task_id", "member_id"]


class TaskMiniSerializer(serializers.ModelSerializer):
    template_application_id = serializers.IntegerField(source="application_id", read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "status", "priority", "due_date", "assigned_to", "template_application_id"]


class TaskRowSerializer(serializers.ModelSerializer):
    checklist = ChecklistItemSerializer(many=True, read_only=True)
    dependencies = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status", "priority", "category", "due_date",
            "assigned_to", "department", "client_id", "checklist", "dependencies",
            "client", "count", "created_at", "updated_at",
        ]

    def get_dependencies(self, obj):
        return TaskDependencyMiniSerializer(obj.dependencies.select_related("depends_on", "depends_on__client"), many=True).data

    def get_client(self, obj):
        if not obj.client_id:
            return None
        return {"id": obj.client_id, "name": obj.client.name, "tradeName": obj.client.trade_name}

    def get_count(self, obj):
        return {
            "subtasks": obj.subtasks.count(),
            "checklist": obj.checklist.count(),
            "comments": obj.comments.count(),
            "followers": obj.followers.count(),
        }


class TaskDetailSerializer(TaskRowSerializer):
    comments = TaskCommentSerializer(many=True, read_only=True)
    followers = TaskFollowerSerializer(many=True, read_only=True)
    dependents = serializers.SerializerMethodField()
    subtasks = serializers.SerializerMethodField()
    template = serializers.SerializerMethodField()
    application = serializers.SerializerMethodField()
    parent_task = serializers.SerializerMethodField()

    class Meta(TaskRowSerializer.Meta):
        fields = TaskRowSerializer.Meta.fields + [
            "completed_at", "assigned_to_id", "reviewer", "recurrence_rule", "recurrence_parent",
            "parent_task_id", "portal_visible", "portal_instructions", "template", "application",
            "comments", "followers", "dependents", "subtasks", "parent_task",
        ]

    def get_dependents(self, obj):
        return TaskDependencyMiniSerializer(obj.dependents.select_related("task"), many=True).data

    def get_subtasks(self, obj):
        return [{"id": t.id, "title": t.title, "status": t.status} for t in obj.subtasks.all()]

    def get_template(self, obj):
        return {"id": obj.template_id, "name": obj.template.name} if obj.template_id else None

    def get_application(self, obj):
        return {"id": obj.application_id, "templateVersionId": obj.application.template_version_id} if obj.application_id else None

    def get_parent_task(self, obj):
        return {"id": obj.parent_task_id, "title": obj.parent_task.title} if obj.parent_task_id else None


class TaskWriteSerializer(NullToBlankMixin, serializers.ModelSerializer):
    NULLABLE_FIELDS = {
        "client", "department", "assigned_to_id", "reviewer", "due_date", "parent_task",
    }
    JSON_OBJECT_FIELDS = {"recurrence_rule"}

    class Meta:
        model = Task
        fields = [
            "client", "title", "description", "priority", "category", "department",
            "assigned_to", "assigned_to_id", "reviewer", "due_date", "recurrence_rule",
            "portal_visible", "portal_instructions", "parent_task", "status",
        ]
        extra_kwargs = {field: {"required": False} for field in fields}
