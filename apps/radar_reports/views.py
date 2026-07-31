from datetime import timedelta

from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.clients.models import ClientCompany, Department
from apps.radar_tasks.models import Task
from apps.radar_documents.models import Document, DocumentRequest
from apps.organizations.models import Membership
from apps.radar_reports.models import ExportJob
from apps.radar_reports.exports import build_export_csv
from apps.storage.services import StorageService


def _period_start(period):
    now = timezone.now()
    if period == "week":
        return now - timedelta(days=7)
    if period == "quarter":
        return now - timedelta(days=90)
    if period == "year":
        return now - timedelta(days=365)
    return now - timedelta(days=30)  # month (default)


class DashboardView(TenantAPIView):
    def get(self, request):
        org = request.tenant
        qp = request.query_params
        period_start = _period_start(qp.get("period", "month"))

        tasks = Task.objects.filter(organization=org)
        clients = ClientCompany.objects.filter(organization=org, is_deleted=False)

        if qp.get("departmentId"):
            tasks = tasks.filter(department_id=qp["departmentId"])
        if qp.get("responsible"):
            tasks = tasks.filter(assigned_to=qp["responsible"])

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        open_statuses = [Task.STATUS_A_FAZER, Task.STATUS_EM_ANDAMENTO, Task.STATUS_AGUARDANDO_CLIENTE, Task.STATUS_AGUARDANDO_TERCEIRO, Task.STATUS_BLOQUEADA]

        open_tasks = tasks.filter(status__in=open_statuses)
        overdue_tasks = open_tasks.filter(due_date__lt=now)
        due_today_tasks = open_tasks.filter(due_date__gte=today_start, due_date__lt=today_end)
        unassigned_tasks = open_tasks.filter(assigned_to_id__isnull=True)

        completed_period = tasks.filter(status=Task.STATUS_CONCLUIDA, completed_at__gte=period_start)
        completed_on_time = completed_period.filter(due_date__isnull=False, completed_at__lte=F("due_date")).count()
        completed_total = completed_period.count()
        completion_rate = round((completed_on_time / completed_total) * 100) if completed_total else 0

        stats = {
            "active_clients": clients.filter(status=ClientCompany.STATUS_ACTIVE).count(),
            "open_tasks": open_tasks.count(),
            "due_today_tasks": due_today_tasks.count(),
            "overdue_tasks": overdue_tasks.count(),
            "unassigned_tasks": unassigned_tasks.count(),
            "pending_documents": Document.objects.filter(organization=org, status__in=[Document.STATUS_SOLICITADO, Document.STATUS_RECEBIDO]).count()
            + DocumentRequest.objects.filter(organization=org, status=DocumentRequest.STATUS_SOLICITADO).count(),
            "completion_rate": completion_rate,
            "new_clients_period": clients.filter(created_at__gte=period_start).count(),
        }

        tasks_by_status = list(tasks.values("status").annotate(count=Count("id")).order_by())
        tasks_by_priority = list(tasks.values("priority").annotate(count=Count("id")).order_by())

        overdue_by_department = list(
            overdue_tasks.filter(department__isnull=False)
            .values(department_name=F("department__name")).annotate(count=Count("id")).order_by("-count")
        )
        overdue_by_department = [{"department": r["department_name"], "count": r["count"]} for r in overdue_by_department]

        def task_item(t):
            return {
                "id": t.id, "title": t.title, "status": t.status, "priority": t.priority, "due_date": t.due_date,
                "client": {"id": t.client_id, "name": t.client.name, "trade_name": t.client.trade_name} if t.client_id else None,
            }

        critical = tasks.filter(status__in=open_statuses, priority__in=[Task.PRIORITY_HIGH, Task.PRIORITY_URGENT]).filter(due_date__lt=today_end).select_related("client").order_by("due_date")[:10]
        upcoming = open_tasks.filter(due_date__gte=today_start, due_date__lte=now + timedelta(days=7)).select_related("client").order_by("due_date")[:10]

        recent_activity = [
            {
                "id": t.id, "action": "complete" if t.status == Task.STATUS_CONCLUIDA else "update",
                "entity": "task", "entity_id": t.id, "detail": t.title,
                "user_name": t.assigned_to or None, "created_at": t.updated_at,
            }
            for t in tasks.order_by("-updated_at")[:10]
        ]

        departments = [{"id": d.id, "name": d.name} for d in Department.objects.filter(organization=org)]
        members = [
            {"id": m.user_id, "name": m.user.get_display_name(), "email": m.user.email}
            for m in Membership.objects.filter(organization=org, status=1).select_related("user")
        ]

        return Response({
            "stats": stats,
            "tasks_by_status": tasks_by_status,
            "tasks_by_priority": tasks_by_priority,
            "overdue_by_department": overdue_by_department,
            "recent_activity": recent_activity,
            "critical_tasks": [task_item(t) for t in critical],
            "upcoming_tasks": [task_item(t) for t in upcoming],
            "overdue_tasks_list": [task_item(t) for t in overdue_tasks.select_related("client")[:20]],
            "filters": {"departments": departments, "members": members},
        })


class ReportsView(TenantAPIView):
    def get(self, request):
        org = request.tenant
        qp = request.query_params
        report_type = qp.get("type", "produtividade")
        date_from = qp.get("from")
        date_to = qp.get("to")

        tasks = Task.objects.filter(organization=org)
        if date_from:
            tasks = tasks.filter(due_date__gte=date_from)
        if date_to:
            tasks = tasks.filter(due_date__lte=date_to)

        if report_type == "carteira":
            clients = ClientCompany.objects.filter(organization=org, is_deleted=False)
            no_templates = clients.filter(template_applications__isnull=True).distinct().values_list("name", flat=True)
            with_delays = clients.filter(radar_tasks__status__in=[Task.STATUS_A_FAZER, Task.STATUS_EM_ANDAMENTO], radar_tasks__due_date__lt=timezone.now()).distinct().values_list("name", flat=True)
            inactive = clients.filter(status=ClientCompany.STATUS_SUSPENDED).values_list("name", flat=True)
            return Response({
                "no_templates": list(no_templates), "with_delays": list(with_delays), "inactive": list(inactive),
            })

        if report_type == "prazos":
            now = timezone.now()
            upcoming = tasks.filter(due_date__gte=now, due_date__lte=now + timedelta(days=30)).select_related("client")
            accumulated = tasks.filter(due_date__lt=now, status__in=[Task.STATUS_A_FAZER, Task.STATUS_EM_ANDAMENTO]).select_related("client")
            return Response({
                "upcoming_count": upcoming.count(),
                "recurring_count": tasks.exclude(recurrence_rule={}).count(),
                "accumulated_count": accumulated.count(),
                "upcoming": [{"title": t.title, "client": t.client.name if t.client_id else None, "due_date": t.due_date, "status": t.status} for t in upcoming[:50]],
                "recurring": [],
                "accumulated": [{"title": t.title, "client": t.client.name if t.client_id else None, "days": (now - t.due_date).days} for t in accumulated[:50]],
            })

        if report_type == "documentos":
            docs = Document.objects.filter(organization=org)
            requests = DocumentRequest.objects.filter(organization=org)
            soon = docs.filter(validity_date__isnull=False, validity_date__lte=timezone.now().date() + timedelta(days=30))
            return Response({
                "requested": requests.filter(status=DocumentRequest.STATUS_SOLICITADO).count(),
                "received": docs.filter(status=Document.STATUS_RECEBIDO).count(),
                "rejected": docs.filter(status=Document.STATUS_REJEITADO).count(),
                "pending": requests.filter(status=DocumentRequest.STATUS_SOLICITADO).count(),
                "expiring_count": soon.count(),
                "expiring": [{"name": d.name, "status": d.status, "days_to_expire": (d.validity_date - timezone.now().date()).days} for d in soon[:50]],
            })

        # produtividade (default)
        completed = tasks.filter(status=Task.STATUS_CONCLUIDA)
        on_time = completed.filter(due_date__isnull=False, completed_at__lte=F("due_date")).count()
        overdue_count = tasks.filter(status__in=[Task.STATUS_A_FAZER, Task.STATUS_EM_ANDAMENTO], due_date__lt=timezone.now()).count()
        person_load = list(
            tasks.exclude(assigned_to="").values("assigned_to")
            .annotate(total=Count("id"), completed=Count("id", filter=Q(status=Task.STATUS_CONCLUIDA)))
            .order_by("-total")[:20]
        )
        return Response({
            "completed": completed.count(),
            "on_time": on_time,
            "overdue": overdue_count,
            "avg_time": None,
            "person_load": [{"name": p["assigned_to"], "completed": p["completed"], "total": p["total"], "avg_time": None} for p in person_load],
        })


class ExportView(TenantAPIView):
    """Gera a exportacao e ja devolve pronta (o volume de dados por
    organizacao aqui e pequeno o bastante pra nao justificar fila do
    Celery + tela de acompanhamento; o ExportJob fica como historico)."""

    def post(self, request):
        export_type = request.data.get("type", "")
        export_format = request.data.get("format", "csv")
        filters = request.data.get("filters") or {}

        job = ExportJob.objects.create(
            organization=request.tenant, type=export_type, format=export_format,
            filters=filters, requested_by=request.user,
        )

        try:
            from django.core.files.base import ContentFile
            content, filename = build_export_csv(request.tenant, export_type, filters)
            key = f"org-{request.tenant.id}/exports/{job.id}-{filename}"
            stored = StorageService.upload_file(
                key=key, data=ContentFile(content), content_type="text/csv",
                organization=request.tenant, uploaded_by=request.user,
            )
            job.stored_object_id = stored["id"]
            job.status = ExportJob.STATUS_COMPLETED
            job.save(update_fields=["stored_object", "status", "updated_at"])
        except Exception as exc:
            job.status = ExportJob.STATUS_FAILED
            job.error_message = str(exc)
            job.save(update_fields=["status", "error_message", "updated_at"])
            return Response({"error": "Falha ao gerar a exportacao."}, status=500)

        from django.core.files.storage import default_storage
        from django.conf import settings as dj_settings
        download_url = default_storage.url(job.stored_object.key)
        internal = getattr(dj_settings, "AWS_S3_ENDPOINT_URL", None)
        if internal and download_url.startswith(internal):
            download_url = "/storage/" + download_url[len(internal):].lstrip("/")

        return Response({
            "id": job.id, "type": job.type, "status": job.status,
            "download_url": download_url, "created_at": job.created_at,
        }, status=201)
