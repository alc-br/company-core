from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import AIProvider


class AIProviderConfig(TimestampMixin):
    provider_name = models.IntegerField(choices=AIProvider.choices, verbose_name=_("Provedor"))
    display_name = models.CharField(max_length=255, verbose_name=_("Nome"))
    api_key_encrypted = models.BinaryField(null=True, blank=True, verbose_name=_("API Key"))
    models_list = models.JSONField(default=dict, blank=True, verbose_name=_("Modelos"))
    is_default = models.BooleanField(default=False, verbose_name=_("Padrão"))
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, null=True, blank=True, related_name="ai_providers", verbose_name=_("Organização"))

    class Meta:
        verbose_name = _("Configuração de Provedor IA")
        verbose_name_plural = _("Configurações de Provedores IA")
        indexes = [models.Index(fields=["provider_name", "is_default"])]

    def __str__(self):
        return f"{self.display_name} ({self.get_provider_name_display()})"


class AIModelConfig(TimestampMixin):
    model_id = models.CharField(max_length=255, verbose_name=_("ID do Modelo"))
    display_name = models.CharField(max_length=255, verbose_name=_("Nome"))
    provider = models.ForeignKey(AIProviderConfig, on_delete=models.CASCADE, related_name="models", verbose_name=_("Provedor"))
    max_tokens = models.PositiveIntegerField(default=4096, verbose_name=_("Max Tokens"))
    cost_per_1k_input = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name=_("Custo/1k Input"))
    cost_per_1k_output = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name=_("Custo/1k Output"))

    class Meta:
        verbose_name = _("Configuração de Modelo IA")
        verbose_name_plural = _("Configurações de Modelos IA")
        unique_together = ["model_id", "provider"]

    def __str__(self):
        return f"{self.display_name} ({self.model_id})"


class AICallLog(TimestampMixin):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="ai_call_logs", verbose_name=_("Organização"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="ai_call_logs", verbose_name=_("Usuário"))
    provider_name = models.CharField(max_length=100, verbose_name=_("Provedor"))
    model = models.CharField(max_length=255, verbose_name=_("Modelo"))
    tokens_input = models.PositiveIntegerField(default=0, verbose_name=_("Tokens Input"))
    tokens_output = models.PositiveIntegerField(default=0, verbose_name=_("Tokens Output"))
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0, verbose_name=_("Custo"))
    latency_ms = models.PositiveIntegerField(default=0, verbose_name=_("Latência (ms)"))
    metadata = models.JSONField(default=dict, blank=True, verbose_name=_("Metadados"))

    class Meta:
        verbose_name = _("Log de Chamada IA")
        verbose_name_plural = _("Logs de Chamadas IA")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "-created_at"]),
            models.Index(fields=["provider_name", "model"]),
        ]

    def __str__(self):
        return f"AI Call: {self.provider_name}/{self.model} ({self.tokens_input + self.tokens_output} tokens)"
