from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import WorkflowExecutionStatus


class Workflow(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    steps_config = models.JSONField(default=list, blank=True, verbose_name=_("Configuração de Etapas"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="workflows",
        verbose_name=_("Organização"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Workflow")
        verbose_name_plural = _("Workflows")

    def __str__(self):
        return self.name


class WorkflowExecution(TimestampMixin):
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="executions",
        verbose_name=_("Workflow"),
    )
    status = models.IntegerField(
        choices=WorkflowExecutionStatus.choices,
        default=WorkflowExecutionStatus.PENDING,
        verbose_name=_("Status"),
    )
    current_step = models.PositiveIntegerField(default=0, verbose_name=_("Etapa Atual"))
    input_data = models.JSONField(default=dict, verbose_name=_("Input"))
    output_data = models.JSONField(default=dict, blank=True, verbose_name=_("Output"))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Início"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Conclusão"))

    class Meta:
        verbose_name = _("Execução de Workflow")
        verbose_name_plural = _("Execuções de Workflows")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.workflow.name} - {self.get_status_display()}"


class WorkflowStepLog(models.Model):
    execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name="step_logs",
        verbose_name=_("Execução"),
    )
    step_name = models.CharField(max_length=255, verbose_name=_("Nome da Etapa"))
    status = models.CharField(max_length=50, verbose_name=_("Status"))
    input_data = models.JSONField(default=dict, verbose_name=_("Input"))
    output_data = models.JSONField(default=dict, blank=True, verbose_name=_("Output"))
    error_message = models.TextField(blank=True, verbose_name=_("Erro"))
    duration_ms = models.PositiveIntegerField(default=0, verbose_name=_("Duração"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))

    class Meta:
        verbose_name = _("Log de Etapa")
        verbose_name_plural = _("Logs de Etapas")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.step_name} - {self.status}"
