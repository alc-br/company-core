from django.db.models import IntegerChoices
from django.utils.translation import gettext_lazy as _


class BaseStatus(IntegerChoices):
    """Base status choices for all models."""
    ACTIVE = 1, _("Ativo")
    INACTIVE = 2, _("Inativo")
    DELETED = 3, _("Deletado")
    ARCHIVED = 4, _("Arquivado")


class BillingCycle(IntegerChoices):
    """Billing cycle choices."""
    MONTHLY = 1, _("Mensal")
    QUARTERLY = 2, _("Trimestral")
    SEMIANNUAL = 3, _("Semestral")
    ANNUAL = 4, _("Anual")


class SubscriptionStatus(IntegerChoices):
    """Subscription status choices."""
    ACTIVE = 1, _("Ativa")
    PAST_DUE = 2, _("Atrasada")
    CANCELED = 3, _("Cancelada")
    TRIALING = 4, _("Em teste")
    PAUSED = 5, _("Pausada")
    UNPAID = 6, _("Não paga")


class MembershipRole(IntegerChoices):
    """Membership role choices."""
    OWNER = 1, _("Proprietário")
    ADMIN = 2, _("Administrador")
    MEMBER = 3, _("Membro")
    VIEWER = 4, _("Visualizador")


class MembershipStatus(IntegerChoices):
    """Membership status choices."""
    ACTIVE = 1, _("Ativo")
    INACTIVE = 2, _("Inativo")
    PENDING = 3, _("Pendente")
    SUSPENDED = 4, _("Suspenso")


class InvitationStatus(IntegerChoices):
    """Invitation status choices."""
    PENDING = 1, _("Pendente")
    ACCEPTED = 2, _("Aceito")
    DECLINED = 3, _("Recusado")
    EXPIRED = 4, _("Expirado")


class AIProvider(IntegerChoices):
    """AI provider choices."""
    OPENAI = 1, _("OpenAI")
    ANTHROPIC = 2, _("Anthropic")
    GEMINI = 3, _("Gemini")


class NotificationChannelType(IntegerChoices):
    """Notification channel type choices."""
    EMAIL = 1, _("Email")
    WEBHOOK = 2, _("Webhook")
    SLACK = 3, _("Slack")
    DISCORD = 4, _("Discord")


class StorageBackendType(IntegerChoices):
    """Storage backend type choices."""
    S3 = 1, _("AWS S3")
    MINIO = 2, _("MinIO")
    R2 = 3, _("Cloudflare R2")
    LOCAL = 4, _("Local")


class WebhookDeliveryStatus(IntegerChoices):
    """Webhook delivery status choices."""
    PENDING = 1, _("Pendente")
    SUCCESS = 2, _("Sucesso")
    FAILED = 3, _("Falhou")
    RETRYING = 4, _("Retentando")
    EXPIRED = 5, _("Expirado")


class WorkflowExecutionStatus(IntegerChoices):
    """Workflow execution status choices."""
    PENDING = 1, _("Pendente")
    RUNNING = 2, _("Em execução")
    COMPLETED = 3, _("Concluído")
    FAILED = 4, _("Falhou")
    PAUSED = 5, _("Pausado")
    CANCELLED = 6, _("Cancelado")


class JobStatus(IntegerChoices):
    """Job status choices."""
    PENDING = 1, _("Pendente")
    RUNNING = 2, _("Em execução")
    COMPLETED = 3, _("Concluído")
    FAILED = 4, _("Falhou")
    RETRYING = 5, _("Retentando")
    DEAD_LETTER = 6, _("Dead Letter")


class MetricType(IntegerChoices):
    """Usage metric type choices."""
    AI_TOKENS = 1, _("Tokens IA")
    AI_REQUESTS = 2, _("Requisições IA")
    API_REQUESTS = 3, _("Requisições API")
    FILE_UPLOAD = 4, _("Upload de Arquivos")
    FILE_DOWNLOAD = 5, _("Download de Arquivos")
    STORAGE_BYTES = 6, _("Bytes Armazenados")
