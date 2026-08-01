import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.radar_tasks.models import Task, ChecklistItem, TaskComment, TaskDependency, TaskFollower
from apps.notifications.api_views import notify_user
from apps.radar_tasks.serializers import TaskRowSerializer, TaskDetailSerializer, TaskWriteSerializer

logger = logging.getLogger(__name__)

# Chaves que disparam uma acao especifica no PUT/PATCH, em vez de update generico de campo.
# Em snake_case: o CamelCaseJSONParser converte o body recebido antes de chegar em request.data.
ACTION_KEYS = {
    "update_status", "add_checklist", "toggle_checklist", "remove_checklist_item",
    "reorder_checklist", "add_comment", "add_dependency", "remove_dependency",
}


class TaskListCreateView(TenantAPIView):
    def get(self, request):
        qs = Task.objects.filter(organization=request.tenant).select_related("client", "department")
        qp = request.query_params

        statuses = qp.get("statuses")
        if statuses:
            qs = qs.filter(status__in=statuses.split(","))
        if qp.get("priority"):
            qs = qs.filter(priority=qp["priority"])
        if qp.get("departmentId"):
            qs = qs.filter(department_id=qp["departmentId"])
        if qp.get("clientId"):
            qs = qs.filter(client_id=qp["clientId"])
        if qp.get("assignedTo"):
            qs = qs.filter(assigned_to=qp["assignedTo"])
        if qp.get("dateFrom"):
            qs = qs.filter(due_date__gte=qp["dateFrom"])
        if qp.get("dateTo"):
            qs = qs.filter(due_date__lte=qp["dateTo"])
        if qp.get("search"):
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=qp["search"]) | Q(description__icontains=qp["search"]))
        if "parentId" in qp:
            parent_id = qp.get("parentId")
            qs = qs.filter(parent_task_id=parent_id) if parent_id else qs.filter(parent_task__isnull=True)
        if qp.get("myQueue") == "true" and not qp.get("assignedTo"):
            qs = qs.filter(assigned_to_id=request.user.id)
        if qp.get("portalVisible") == "true":
            qs = qs.filter(portal_visible=True)
            if qp.get("clientId"):
                qs = qs.filter(client_id=qp["clientId"])

        limit = qp.get("limit")
        qs = qs.order_by("-created_at")
        if limit:
            qs = qs[: int(limit)]

        return Response(TaskRowSerializer(qs, many=True).data)

    def post(self, request):
        data = dict(request.data)
        checklist_data = data.pop("checklist", None)
        data.pop("tags", None)  # tags de tarefa nao modeladas ainda; ignorado com seguranca
        recurrence_rule = data.get("recurrence_rule")
        if isinstance(recurrence_rule, str):
            import json
            try:
                data["recurrence_rule"] = json.loads(recurrence_rule) if recurrence_rule else {}
            except ValueError:
                data["recurrence_rule"] = {}

        serializer = TaskWriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(organization=request.tenant)

        if checklist_data:
            for i, item in enumerate(checklist_data):
                ChecklistItem.objects.create(
                    organization=request.tenant, task=task,
                    text=item.get("text", ""), required=item.get("required", False), order=i,
                )

        _notify_assignment(request, task)
        return Response(TaskDetailSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(TenantAPIView):
    def get_object(self, request, pk):
        return get_object_or_404(Task, pk=pk, organization=request.tenant)

    def get(self, request, pk):
        return Response(TaskDetailSerializer(self.get_object(request, pk)).data)

    def put(self, request, pk):
        return self._dispatch(request, pk)

    def patch(self, request, pk):
        return self._dispatch(request, pk)

    def _dispatch(self, request, pk):
        task = self.get_object(request, pk)
        body = request.data

        if any(k in body for k in ACTION_KEYS):
            error = self._apply_actions(request, task, body)
            if error:
                return Response({"error": error}, status=status.HTTP_200_OK)
            return Response(TaskDetailSerializer(task).data)

        # status direto (meu-trabalho usa PATCH {status,...}) ou update_status explicito
        new_status = body.get("update_status") or body.get("status")
        if new_status:
            error = self._transition_status(task, new_status)
            if error:
                return Response({"error": error}, status=status.HTTP_200_OK)

        write_fields = {k: v for k, v in body.items() if k not in ("update_status", "status")}
        serializer = TaskWriteSerializer(task, data=write_fields, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(TaskDetailSerializer(task).data)

    def _apply_actions(self, request, task, body):
        if "update_status" in body:
            error = self._transition_status(task, body["update_status"])
            if error:
                return error

        if "due_date" in body:
            task.due_date = body["due_date"]
            task.save(update_fields=["due_date", "updated_at"])

        if "assigned_to" in body or "assigned_to_id" in body:
            previous_assignee_id = task.assigned_to_id
            if "assigned_to" in body:
                task.assigned_to = body["assigned_to"]
            if "assigned_to_id" in body:
                task.assigned_to_id = body["assigned_to_id"]
            task.save(update_fields=["assigned_to", "assigned_to_id", "updated_at"])
            if task.assigned_to_id and task.assigned_to_id != previous_assignee_id:
                _notify_assignment(request, task)

        if "add_checklist" in body:
            existing = task.checklist.count()
            for i, item in enumerate(body["add_checklist"]):
                ChecklistItem.objects.create(
                    organization=task.organization, task=task,
                    text=item.get("text", ""), required=item.get("required", False),
                    order=existing + i,
                )

        if "toggle_checklist" in body:
            item = task.checklist.filter(pk=body["toggle_checklist"]).first()
            if item:
                item.done = not item.done
                item.save(update_fields=["done", "updated_at"])

        if "remove_checklist_item" in body:
            task.checklist.filter(pk=body["remove_checklist_item"]).delete()

        if "reorder_checklist" in body:
            for entry in body["reorder_checklist"]:
                task.checklist.filter(pk=entry["id"]).update(order=entry["order"])

        if "add_comment" in body:
            c = body["add_comment"]
            TaskComment.objects.create(
                organization=task.organization, task=task,
                user_id=c.get("user_id") or request.user.id,
                user_name=c.get("user_name") or request.user.get_display_name(),
                content=c.get("content", ""),
            )

        if "add_dependency" in body:
            depends_on = Task.objects.filter(pk=body["add_dependency"], organization=task.organization).first()
            if depends_on and depends_on.id != task.id:
                TaskDependency.objects.get_or_create(organization=task.organization, task=task, depends_on=depends_on)

        if "remove_dependency" in body:
            task.dependencies.filter(depends_on_id=body["remove_dependency"]).delete()

        return None

    def _transition_status(self, task, new_status):
        new_status = Task.normalize_status(new_status)
        valid_statuses = dict(Task.STATUS_CHOICES)
        if new_status not in valid_statuses:
            return f"Status invalido: {new_status}"

        if new_status == Task.STATUS_CONCLUIDA:
            if task.status == Task.STATUS_BLOQUEADA:
                return "Tarefa bloqueada nao pode ser concluida."
            pending_required = task.checklist.filter(required=True, done=False).exists()
            if pending_required:
                return "Existem itens obrigatorios do checklist ainda nao concluidos."
            task.completed_at = timezone.now()
        else:
            task.completed_at = None

        task.status = new_status
        task.save(update_fields=["status", "completed_at", "updated_at"])
        return None


class TaskCommentListCreateView(TenantAPIView):
    """Sub-recurso usado pelo portal (POST /tasks/{id}/comments)."""

    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, organization=request.tenant)
        TaskComment.objects.create(
            organization=request.tenant, task=task,
            user_id=request.user.id if request.user.is_authenticated else None,
            user_name=request.data.get("user_name") or "",
            content=request.data.get("content", ""),
        )
        from apps.radar_tasks.serializers import TaskCommentSerializer
        return Response(TaskCommentSerializer(task.comments.all(), many=True).data, status=status.HTTP_201_CREATED)


def _notify_assignment(request, task):
    """Notifica o responsavel designado, exceto quando ele mesmo fez a atribuicao.

    Atencao: 'assigned_to_id' e o nome literal do campo ForeignKey (o nome
    display em texto livre e 'assigned_to') — o atributo ja retorna a
    instancia de CustomUser, nao um inteiro.
    """
    assignee = task.assigned_to_id
    if not assignee or assignee.id == request.user.id:
        return
    notify_user(
        organization=task.organization, user=assignee,
        title="Nova tarefa atribuida a voce", message=task.title,
        type="task_assigned", link=f"/app/tarefas/{task.id}",
    )


class TaskFollowView(TenantAPIView):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk, organization=request.tenant)
        TaskFollower.objects.get_or_create(organization=request.tenant, task=task, member=request.user)
        return Response({"success": True}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk, organization=request.tenant)
        task.followers.filter(member=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
