from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin


class Agent(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    system_prompt = models.TextField(verbose_name=_("System Prompt"))
    provider = models.ForeignKey("ai.AIProviderConfig", on_delete=models.SET_NULL, null=True, verbose_name=_("Provedor"))
    model_id = models.CharField(max_length=255, default="gpt-4o", verbose_name=_("Modelo"))
    temperature = models.FloatField(default=0.7, verbose_name=_("Temperatura"))
    memory_config = models.JSONField(default=dict, blank=True, verbose_name=_("Configuração de Memória"))
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="agents", verbose_name=_("Organização"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    tools = models.ManyToManyField("AgentTool", blank=True, related_name="agents", verbose_name=_("Ferramentas"))

    class Meta:
        verbose_name = _("Agente")
        verbose_name_plural = _("Agentes")
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "is_active"])]

    def __str__(self):
        return self.name


class AgentTool(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    code = models.CharField(max_length=255, unique=True, verbose_name=_("Código"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    handler_path = models.CharField(max_length=500, verbose_name=_("Handler Path"))
    input_schema = models.JSONField(default=dict, blank=True, verbose_name=_("Schema de Input"))

    class Meta:
        verbose_name = _("Ferramenta de Agente")
        verbose_name_plural = _("Ferramentas de Agentes")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class AgentExecution(TimestampMixin):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="executions", verbose_name=_("Agente"))
    status = models.CharField(max_length=50, default="pending", verbose_name=_("Status"))
    input_data = models.JSONField(default=dict, verbose_name=_("Input"))
    output_data = models.JSONField(default=dict, blank=True, verbose_name=_("Output"))
    tokens_used = models.PositiveIntegerField(default=0, verbose_name=_("Tokens"))
    duration_ms = models.PositiveIntegerField(default=0, verbose_name=_("Duração"))
    error_message = models.TextField(blank=True, verbose_name=_("Erro"))

    class Meta:
        verbose_name = _("Execução de Agente")
        verbose_name_plural = _("Execuções de Agentes")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Agent '{self.agent.name}' execution ({self.status})"
