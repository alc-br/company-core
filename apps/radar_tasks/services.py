import logging
from datetime import timedelta, date
from django.db import transaction

from apps.radar_tasks.models import Task, ChecklistItem
from apps.clients.models import Department
from apps.organizations.models import Membership

logger = logging.getLogger(__name__)


def _resolve_department(organization, ref):
    if not ref:
        return None
    if isinstance(ref, int) or (isinstance(ref, str) and ref.isdigit()):
        dept = Department.objects.filter(organization=organization, pk=int(ref)).first()
        if dept:
            return dept
    return Department.objects.filter(organization=organization, name__iexact=str(ref)).first()


def _resolve_assignee(organization, role_mappings, department_ref, role_ref):
    """Resolve o usuario mapeado no wizard 'Aplicar Template' (Step 3).

    role_mappings vem do TemplateApplication (ver TemplateApplicationWriteSerializer)
    com as MESMAS chaves que o wizard usa em aplicar-template/page.tsx: o
    papel bruto da tarefa, ou 'dept_<department bruto>'. Os valores sao ids
    de Membership no formato 'm-<id>' (retornados por /api/v1/team), nao ids
    de User direto.
    """
    if not role_mappings:
        return None

    value = None
    if role_ref:
        value = role_mappings.get(str(role_ref))
    if not value and department_ref:
        value = role_mappings.get(f"dept_{department_ref}")
    if not value:
        return None

    membership_id = str(value).removeprefix("m-")
    if not membership_id.isdigit():
        return None

    membership = Membership.objects.filter(pk=int(membership_id), organization=organization).select_related("user").first()
    return membership.user if membership else None


def _compute_due_date(base_date: date, rule: dict):
    """Resolve a data de uma TemplateTask a partir da data-base da aplicacao.

    Cobre os tipos mais comuns de TMP-04. Tipos nao reconhecidos ou regra
    ausente caem na propria data-base (nunca deixa a tarefa sem data por um
    tipo desconhecido silenciosamente virar erro).
    """
    if not rule or not isinstance(rule, dict):
        return base_date

    rule_type = rule.get("type")
    value = rule.get("value")

    try:
        value = int(value) if value is not None else 0
    except (TypeError, ValueError):
        value = 0

    # Os tipos reais (options do <Select> em templates/[id]/page.tsx) sao
    # base_date/days_before/days_after/fixed_month_day/no_deadline — os
    # aliases extras abaixo cobrem nomes anteriores/alternativos ja vistos
    # em payloads manuais, mas o contrato de verdade e o do frontend.
    if rule_type in ("no_deadline", "sem_prazo"):
        return None
    if rule_type in ("base_date", "on_base_date", "na_data_base"):
        return base_date
    if rule_type in ("days_before", "days_before_base"):
        return base_date - timedelta(days=value)
    if rule_type in ("days_after", "days_after_base", "days_after_application"):
        return base_date + timedelta(days=value)
    if rule_type in ("fixed_month_day", "fixed_day_of_month"):
        import calendar
        day = min(value or base_date.day, calendar.monthrange(base_date.year, base_date.month)[1])
        return base_date.replace(day=day)
    return base_date


@transaction.atomic
def generate_tasks_from_application(application):
    """Cria as tarefas reais (Task) a partir do snapshot de etapas da versao aplicada.

    Se algo falhar no meio, a transacao inteira desfaz (nenhuma tarefa parcial
    fica orfa) — regra explicita da especificacao (secao 8.2).
    """
    stages = application.template_version.stages_snapshot or []
    organization = application.organization
    created = []

    for stage in stages:
        for task_def in stage.get("tasks", []) or []:
            # 'stages' e um JSONField livre, mas passa pelo CamelCaseJSONParser
            # global igual qualquer outro body de request — as chaves internas
            # (dueDateRule, portalVisible, portalInstructions) chegam aqui ja
            # convertidas para snake_case. Ler a versao camelCase aqui sempre
            # falhava silenciosamente e a tarefa caia na data-base.
            due_date_rule = task_def.get("due_date_rule") or task_def.get("dueDateRule") or {}
            due_date = _compute_due_date(application.base_date, due_date_rule)
            department = _resolve_department(organization, task_def.get("department"))
            portal_visible = task_def.get("portal_visible", task_def.get("portalVisible"))
            portal_instructions = task_def.get("portal_instructions", task_def.get("portalInstructions", ""))
            assignee = _resolve_assignee(
                organization, application.role_mappings, task_def.get("department"), task_def.get("role"),
            )

            task = Task.objects.create(
                organization=organization,
                client=application.client,
                title=task_def.get("title", "Tarefa"),
                description=task_def.get("description", ""),
                priority=task_def.get("priority", Task.PRIORITY_MEDIUM),
                category=stage.get("name", ""),
                department=department,
                assigned_to_id=assignee,
                assigned_to=assignee.get_display_name() if assignee else "",
                due_date=due_date,
                template=application.template,
                application=application,
                portal_visible=bool(portal_visible),
                portal_instructions=portal_instructions,
            )
            for i, item in enumerate(task_def.get("checklist", []) or []):
                ChecklistItem.objects.create(
                    organization=organization, task=task,
                    text=item.get("text", ""), required=bool(item.get("required")), order=i,
                )
            created.append(task)

    logger.info(f"Aplicacao {application.id}: {len(created)} tarefas geradas.")
    return created
