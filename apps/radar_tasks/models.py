from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TenantMixin, TimestampMixin


class Task(TenantMixin, TimestampMixin):
    STATUS_A_FAZER = "a_fazer"
    STATUS_EM_ANDAMENTO = "em_andamento"
    STATUS_CONCLUIDA = "concluida"
    STATUS_AGUARDANDO_CLIENTE = "aguardando_cliente"
    STATUS_AGUARDANDO_TERCEIRO = "aguardando_terceiro"
    STATUS_BLOQUEADA = "bloqueada"
    STATUS_CANCELADA = "cancelada"
    STATUS_CHOICES = [
        (STATUS_A_FAZER, _("A fazer")),
        (STATUS_EM_ANDAMENTO, _("Em andamento")),
        (STATUS_CONCLUIDA, _("Concluida")),
        (STATUS_AGUARDANDO_CLIENTE, _("Aguardando cliente")),
        (STATUS_AGUARDANDO_TERCEIRO, _("Aguardando terceiro")),
        (STATUS_BLOQUEADA, _("Bloqueada")),
        (STATUS_CANCELADA, _("Cancelada")),
    ]
    # aceito na entrada e normalizado para o valor acima (o portal manda acentuado)
    STATUS_ALIASES = {"concluído": STATUS_CONCLUIDA, "concluido": STATUS_CONCLUIDA}

    PRIORITY_LOW = "low"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_HIGH = "high"
    PRIORITY_URGENT = "urgent"
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, _("Baixa")),
        (PRIORITY_MEDIUM, _("Media")),
        (PRIORITY_HIGH, _("Alta")),
        (PRIORITY_URGENT, _("Urgente")),
    ]

    title = models.CharField(max_length=255, verbose_name=_("Titulo"))
    description = models.TextField(blank=True, verbose_name=_("Descricao"))
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_A_FAZER, verbose_name=_("Status"))
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM, verbose_name=_("Prioridade"))
    category = models.CharField(max_length=100, blank=True, verbose_name=_("Categoria"))

    client = models.ForeignKey(
        "clients.ClientCompany", on_delete=models.CASCADE, null=True, blank=True,
        related_name="radar_tasks", verbose_name=_("Cliente"),
    )
    department = models.ForeignKey(
        "clients.Department", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tasks", verbose_name=_("Departamento"),
    )
    assigned_to = models.CharField(max_length=150, blank=True, verbose_name=_("Responsavel (nome)"))
    assigned_to_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_tasks", verbose_name=_("Responsavel"),
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewing_tasks", verbose_name=_("Revisor"),
    )

    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Prazo"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Concluida em"))

    template = models.ForeignKey(
        "radar_templates.Template", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="generated_tasks", verbose_name=_("Template de origem"),
    )
    application = models.ForeignKey(
        "radar_templates.TemplateApplication", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tasks", verbose_name=_("Aplicacao de origem"),
    )

    recurrence_rule = models.JSONField(default=dict, blank=True, verbose_name=_("Regra de recorrencia"))
    recurrence_parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="recurrence_children", verbose_name=_("Serie recorrente (origem)"),
    )
    parent_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="subtasks", verbose_name=_("Tarefa-mae"),
    )

    portal_visible = models.BooleanField(default=False, verbose_name=_("Visivel no portal"))
    portal_instructions = models.TextField(blank=True, verbose_name=_("Instrucoes para o cliente"))

    class Meta:
        verbose_name = _("Tarefa")
        verbose_name_plural = _("Tarefas")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "due_date"]),
            models.Index(fields=["organization", "client"]),
        ]

    def __str__(self):
        return self.title

    @classmethod
    def normalize_status(cls, value):
        return cls.STATUS_ALIASES.get(value, value)


class ChecklistItem(TenantMixin, TimestampMixin):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="checklist", verbose_name=_("Tarefa"))
    text = models.CharField(max_length=255, verbose_name=_("Texto"))
    done = models.BooleanField(default=False, verbose_name=_("Concluido"))
    required = models.BooleanField(default=False, verbose_name=_("Obrigatorio"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordem"))

    class Meta:
        verbose_name = _("Item de checklist")
        verbose_name_plural = _("Itens de checklist")
        ordering = ["order", "id"]


class TaskComment(TenantMixin, TimestampMixin):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments", verbose_name=_("Tarefa"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+",
    )
    user_name = models.CharField(max_length=150, blank=True, verbose_name=_("Autor (nome)"))
    content = models.TextField(verbose_name=_("Conteudo"))

    class Meta:
        verbose_name = _("Comentario")
        verbose_name_plural = _("Comentarios")
        ordering = ["created_at"]


class TaskDependency(TenantMixin, TimestampMixin):
    BLOCKING = "blocking"
    INFORMATIONAL = "informational"
    TYPE_CHOICES = [(BLOCKING, _("Bloqueante")), (INFORMATIONAL, _("Informativa"))]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="dependencies", verbose_name=_("Tarefa"))
    depends_on = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="dependents", verbose_name=_("Depende de"))
    blocking_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=BLOCKING, verbose_name=_("Tipo"))

    class Meta:
        verbose_name = _("Dependencia de tarefa")
        verbose_name_plural = _("Dependencias de tarefa")
        unique_together = ["task", "depends_on"]


class TaskFollower(TenantMixin, TimestampMixin):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="followers", verbose_name=_("Tarefa"))
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+", verbose_name=_("Membro"))

    class Meta:
        verbose_name = _("Seguidor de tarefa")
        verbose_name_plural = _("Seguidores de tarefa")
        unique_together = ["task", "member"]
