"""Endpoints de dados do Portal do Cliente — /api/v1/portal/*.

Antes desta troca, o frontend do portal chamava direto os endpoints de
staff (/api/tasks, /api/documents, /api/document-requests, /api/calendar),
que exigem TenantAPIView (IsAuthenticated + request.tenant resolvido via
sessao Django de funcionario). A sessao do portal e outra (portal_contact_id
na sessao), entao TODAS essas chamadas voltavam 403 — o portal inteiro
(exceto login/logout/anuncios) parecia "vazio" mas na verdade toda
requisicao de dado falhava silenciosamente.

Regra de seguranca de todo view aqui: o cliente/organizacao SEMPRE vem da
sessao do contato autenticado, nunca de query param — mesmo que o
frontend mande clientId, ele e ignorado. Mesmo padrao ja usado em
AnnouncementListView.
"""
import logging

from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime, parse_date
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.radar_portal.views import _get_portal_contact

logger = logging.getLogger(__name__)


class PortalAPIView(APIView):
    """Base para endpoints de dados do portal: exige sessao de contato
    valida e disponibiliza self.contact / self.client / self.org."""

    permission_classes = [AllowAny]
    versioning_class = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        contact = _get_portal_contact(request)
        if not contact:
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed("Sessão do portal inválida.")
        self.contact = contact
        self.client = contact.client
        self.org = contact.client.organization


def _serialize_portal_task(t):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "due_date": t.due_date,
        "portal_instructions": t.portal_instructions,
        "client_name": t.client.name if t.client_id else None,
        "priority": t.priority,
    }


class PortalTaskListView(PortalAPIView):
    def get(self, request):
        from apps.radar_tasks.models import Task

        tasks = Task.objects.filter(
            organization=self.org, client=self.client, portal_visible=True,
        ).exclude(status=Task.STATUS_CANCELADA).order_by("due_date")
        return Response([_serialize_portal_task(t) for t in tasks])


class PortalTaskDetailView(PortalAPIView):
    def put(self, request, pk):
        from apps.radar_tasks.models import Task

        task = get_object_or_404(Task, pk=pk, organization=self.org, client=self.client, portal_visible=True)
        new_status = request.data.get("status")
        if Task.normalize_status(new_status) != Task.STATUS_CONCLUIDA:
            return Response({"error": "O portal só pode marcar a tarefa como concluída."}, status=status.HTTP_400_BAD_REQUEST)

        pending_required = task.checklist.filter(required=True, done=False).exists()
        if pending_required:
            return Response({"error": "Existem itens obrigatórios do checklist ainda não concluídos."}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        task.status = Task.STATUS_CONCLUIDA
        task.completed_at = timezone.now()
        task.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(_serialize_portal_task(task))


class PortalTaskCommentView(PortalAPIView):
    def post(self, request, pk):
        from apps.radar_tasks.models import Task, TaskComment

        task = get_object_or_404(Task, pk=pk, organization=self.org, client=self.client, portal_visible=True)
        content = (request.data.get("content") or "").strip()
        if not content:
            return Response({"error": "Comentário vazio."}, status=status.HTTP_400_BAD_REQUEST)

        TaskComment.objects.create(
            organization=self.org, task=task, user=None,
            user_name=self.contact.name, content=content,
        )
        return Response({"success": True}, status=status.HTTP_201_CREATED)


class PortalDocumentRequestListView(PortalAPIView):
    def get(self, request):
        from apps.radar_documents.models import DocumentRequest

        qs = DocumentRequest.objects.filter(organization=self.org, client=self.client).order_by("-created_at")
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        data = [
            {
                "id": r.id, "title": r.title, "instructions": r.instructions,
                "due_date": r.due_date, "accepted_formats": r.accepted_formats,
                "status": r.status, "created_at": r.created_at,
            }
            for r in qs
        ]
        return Response({"requests": data})


class PortalDocumentListView(PortalAPIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        from apps.radar_documents.models import Document

        qs = Document.objects.filter(organization=self.org, client=self.client).select_related("document_type").order_by("-created_at")
        data = []
        for d in qs:
            data.append({
                "id": d.id, "name": d.name, "status": d.status,
                "document_type": {"name": d.document_type.name} if d.document_type_id else None,
                "updated_at": d.updated_at,
            })
        return Response({"documents": data})

    def post(self, request):
        from apps.radar_documents.models import Document, DocumentRequest
        from apps.storage.services import StorageService

        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "Arquivo obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        key = f"org-{self.org.id}/clients/{self.client.id}/documents/{file_obj.name}"
        StorageService.upload_file(
            key=key, data=file_obj, content_type=file_obj.content_type,
            organization=self.org, uploaded_by=None,
        )

        task_id = request.data.get("taskId")
        task = None
        if task_id:
            from apps.radar_tasks.models import Task
            task = Task.objects.filter(pk=task_id, organization=self.org, client=self.client).first()

        request_id = request.data.get("requestId")
        doc_request = None
        if request_id:
            doc_request = DocumentRequest.objects.filter(pk=request_id, organization=self.org, client=self.client).first()

        from apps.storage.models import StoredObject
        stored = StoredObject.objects.filter(key=key, organization=self.org).order_by("-created_at").first()

        document = Document.objects.create(
            organization=self.org, client=self.client,
            name=request.data.get("name") or file_obj.name,
            status=Document.STATUS_RECEBIDO,
            stored_object=stored, task=task, request=doc_request,
        )
        if doc_request:
            doc_request.status = DocumentRequest.STATUS_RECEBIDO
            doc_request.save(update_fields=["status", "updated_at"])

        return Response({"id": document.id, "name": document.name, "status": document.status}, status=status.HTTP_201_CREATED)


class PortalCalendarView(PortalAPIView):
    def get(self, request):
        from apps.radar_tasks.models import Task

        qp = request.query_params
        start = qp.get("start")
        end = qp.get("end")
        start = (parse_datetime(start) or parse_date(start)) if start else None
        end = (parse_datetime(end) or parse_date(end)) if end else None

        tasks = Task.objects.filter(
            organization=self.org, client=self.client, due_date__isnull=False,
        ).exclude(status=Task.STATUS_CANCELADA)
        if start:
            tasks = tasks.filter(due_date__gte=start)
        if end:
            tasks = tasks.filter(due_date__lte=end)

        events = [
            {
                "id": f"task-{t.id}", "title": t.title, "description": t.description,
                "startDate": t.due_date, "endDate": None, "allDay": True, "color": None,
                "type": "deadline" if t.status == Task.STATUS_A_FAZER else "task",
                "clientName": t.client.name,
            }
            for t in tasks[:200]
        ]
        return Response({"events": events})


class PortalProfileView(PortalAPIView):
    def get(self, request):
        c = self.contact
        return Response({"name": c.name, "email": c.email, "phone": c.phone})

    def put(self, request):
        c = self.contact
        if "name" in request.data and (request.data["name"] or "").strip():
            c.name = request.data["name"].strip()
        if "phone" in request.data:
            c.phone = request.data["phone"] or ""
        c.save(update_fields=["name", "phone", "updated_at"])
        return Response({"name": c.name, "email": c.email, "phone": c.phone})


class PortalChangePasswordView(PortalAPIView):
    def post(self, request):
        current = request.data.get("current") or ""
        new_pass = request.data.get("new_pass") or ""
        if not self.contact.password_hash or not check_password(current, self.contact.password_hash):
            return Response({"error": "Senha atual incorreta."}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_pass) < 8:
            return Response({"error": "A nova senha deve ter no mínimo 8 caracteres."}, status=status.HTTP_400_BAD_REQUEST)

        self.contact.password_hash = make_password(new_pass)
        self.contact.save(update_fields=["password_hash", "updated_at"])
        return Response({"success": True})
