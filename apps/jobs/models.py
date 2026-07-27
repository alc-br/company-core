from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import JobStatus


class Job(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    task_path = models.CharField(max_length=500, verbose_name=_("Task Path"))
    status = models.IntegerField(
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
        verbose_name=_("Status"),
    )
    priority = models.IntegerField(default=5, verbose_name=_("Prioridade"))
    retries = models.PositiveIntegerField(default=0, verbose_name=_("Retries"))
    max_retries = models.PositiveIntegerField(default=3, verbose_name=_("Max Retries"))
    last_error = models.TextField(blank=True, verbose_name=_("Último Erro"))
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Agendado"))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Início"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Conclusão"))
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
        verbose_name=_("Organização"),
    )

    class Meta:
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")
        ordering = ["priority", "-created_at"]
        indexes = [models.Index(fields=["status", "priority"])]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
