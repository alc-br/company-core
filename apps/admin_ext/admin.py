from django.contrib import admin
from apps.organizations.models import Organization, Membership, Invitation
from apps.billing.models import Plan, Subscription, Invoice
from apps.quotas.models import QuotaDefinition, QuotaAllocation
from apps.ai.models import AIProviderConfig, AIModelConfig, AICallLog
from apps.agents.models import Agent, AgentTool, AgentExecution
from apps.audit.models import AuditLog
from apps.notifications.models import NotificationChannel, NotificationTemplate, NotificationLog
from apps.webhooks.models import WebhookEndpoint, WebhookDelivery
from apps.storage.models import StorageBackendConfig, StoredObject
from apps.jobs.models import Job
from apps.usage.models import UsageRecord
from apps.analytics.models import AnalyticsEvent

admin.site.register(Organization)
admin.site.register(Membership)
admin.site.register(Invitation)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(Invoice)
admin.site.register(QuotaDefinition)
admin.site.register(QuotaAllocation)
admin.site.register(AIProviderConfig)
admin.site.register(AIModelConfig)
admin.site.register(AICallLog)
admin.site.register(Agent)
admin.site.register(AgentTool)
admin.site.register(AgentExecution)
admin.site.register(AuditLog)
admin.site.register(NotificationChannel)
admin.site.register(NotificationTemplate)
admin.site.register(NotificationLog)
admin.site.register(WebhookEndpoint)
admin.site.register(WebhookDelivery)
admin.site.register(StorageBackendConfig)
admin.site.register(StoredObject)
admin.site.register(Job)
admin.site.register(UsageRecord)
admin.site.register(AnalyticsEvent)
