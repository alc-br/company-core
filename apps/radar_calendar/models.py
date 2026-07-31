from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TenantMixin, TimestampMixin


class Holiday(TenantMixin, TimestampMixin):
    name = models.CharField(max_length=150, verbose_name=_("Nome"))
    date = models.DateField(verbose_name=_("Data"))
    recurring_yearly = models.BooleanField(default=False, verbose_name=_("Recorrente todo ano"))

    class Meta:
        verbose_name = _("Feriado")
        verbose_name_plural = _("Feriados")
        ordering = ["date"]


class CalendarEvent(TenantMixin, TimestampMixin):
    TYPE_MEETING = "meeting"
    TYPE_OTHER = "other"
    TYPE_CHOICES = [(TYPE_MEETING, _("Reuniao")), (TYPE_OTHER, _("Outro"))]

    title = models.CharField(max_length=255, verbose_name=_("Titulo"))
    description = models.TextField(blank=True, verbose_name=_("Descricao"))
    start_date = models.DateTimeField(verbose_name=_("Inicio"))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Fim"))
    all_day = models.BooleanField(default=False, verbose_name=_("Dia inteiro"))
    color = models.CharField(max_length=20, blank=True, verbose_name=_("Cor"))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_MEETING, verbose_name=_("Tipo"))
    client = models.ForeignKey(
        "clients.ClientCompany", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="calendar_events", verbose_name=_("Cliente"),
    )

    class Meta:
        verbose_name = _("Evento")
        verbose_name_plural = _("Eventos")
        ordering = ["start_date"]
        indexes = [models.Index(fields=["organization", "start_date"])]

    def __str__(self):
        return self.title
