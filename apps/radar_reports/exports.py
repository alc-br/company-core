import csv
import io
from datetime import timedelta

from django.utils import timezone

from apps.clients.models import ClientCompany
from apps.radar_tasks.models import Task
from apps.radar_documents.models import Document, DocumentRequest


def _csv_bytes(header, rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8-sig")  # BOM: acentos abrem certo no Excel


def build_export_csv(organization, export_type, filters):
    """Gera o CSV de uma exportacao. Retorna (bytes, nome_do_arquivo)."""
    filters = filters or {}

    if export_type in ("documents", "documentos"):
        qs = Document.objects.filter(organization=organization).select_related("client", "document_type")
        if filters.get("client_id"):
            qs = qs.filter(client_id=filters["client_id"])
        if filters.get("type_id"):
            qs = qs.filter(document_type_id=filters["type_id"])
        if filters.get("status"):
            qs = qs.filter(status=filters["status"])
        rows = [
            [d.name, d.client.name, d.document_type.name if d.document_type_id else "", d.status, d.validity_date or "", d.created_at]
            for d in qs
        ]
        return _csv_bytes(["Documento", "Cliente", "Tipo", "Status", "Validade", "Criado em"], rows), "documentos.csv"

    if export_type == "produtividade":
        tasks = Task.objects.filter(organization=organization)
        if filters.get("from"):
            tasks = tasks.filter(due_date__gte=filters["from"])
        if filters.get("to"):
            tasks = tasks.filter(due_date__lte=filters["to"])
        rows = [
            [t.title, t.client.name if t.client_id else "", t.assigned_to, t.status, t.priority, t.due_date or "", t.completed_at or ""]
            for t in tasks.select_related("client")
        ]
        return _csv_bytes(["Tarefa", "Cliente", "Responsavel", "Status", "Prioridade", "Prazo", "Concluida em"], rows), "produtividade.csv"

    if export_type == "carteira":
        clients = ClientCompany.objects.filter(organization=organization, is_deleted=False)
        rows = [[c.name, c.trade_name, c.status, c.responsible.get_display_name() if c.responsible_id else "", c.created_at] for c in clients]
        return _csv_bytes(["Razao Social", "Nome Fantasia", "Status", "Responsavel", "Criado em"], rows), "carteira.csv"

    if export_type == "prazos":
        now = timezone.now()
        tasks = Task.objects.filter(organization=organization, due_date__isnull=False).select_related("client")
        if filters.get("from"):
            tasks = tasks.filter(due_date__gte=filters["from"])
        if filters.get("to"):
            tasks = tasks.filter(due_date__lte=filters["to"])
        rows = [
            [t.title, t.client.name if t.client_id else "", t.due_date, t.status,
             (now - t.due_date).days if t.due_date < now and t.status not in (Task.STATUS_CONCLUIDA, Task.STATUS_CANCELADA) else ""]
            for t in tasks
        ]
        return _csv_bytes(["Tarefa", "Cliente", "Prazo", "Status", "Dias em atraso"], rows), "prazos.csv"

    if export_type == "audit":
        from apps.audit.models import AuditLog
        logs = AuditLog.objects.filter(organization=organization).select_related("actor").order_by("-created_at")[:5000]
        rows = [
            [l.created_at, l.actor.get_display_name() if l.actor_id else "Sistema", l.action, l.target_type, l.target_id, l.ip_address or ""]
            for l in logs
        ]
        return _csv_bytes(["Data", "Usuario", "Acao", "Tipo do alvo", "ID do alvo", "IP"], rows), "auditoria.csv"

    # tipo desconhecido: exportacao vazia em vez de erro, para nao travar a UI
    return _csv_bytes(["Sem dados"], []), f"{export_type}.csv"
