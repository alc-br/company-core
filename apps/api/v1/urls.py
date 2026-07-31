"""
API v1 URL configuration.

Centralizes all DRF ViewSet registrations for all Company Core modules.
Each ViewSet is registered with the DefaultRouter for automatic URL generation.
"""
from rest_framework.routers import DefaultRouter

# ─── Core Modules (Group A) ───────────────────────────────────────
from apps.organizations.views import (
    OrganizationViewSet,
    MembershipViewSet,
    InvitationViewSet,
)
from apps.billing.views import (
    PlanViewSet,
    SubscriptionViewSet,
    InvoiceViewSet,
)
from apps.quotas.views import (
    QuotaDefinitionViewSet,
    QuotaAllocationViewSet,
)
from apps.permissions.views import (
    PermissionViewSet,
    RoleViewSet,
    RolePermissionViewSet,
)
from apps.audit.views import (
    AuditLogViewSet,
)
from apps.feature_flags.views import (
    FeatureFlagViewSet,
    FeatureFlagAssignmentViewSet,
)
from apps.settings.views import (
    TenantSettingViewSet,
    GlobalSettingViewSet,
)
from apps.users.views import (
    UserViewSet,
)

# ─── Infrastructure & AI Modules (Group B) ─────────────────────────
from apps.notifications.views import (
    NotificationChannelViewSet,
    NotificationTemplateViewSet,
    NotificationLogViewSet,
)
from apps.storage.views import (
    StorageBackendConfigViewSet,
    StoredObjectViewSet,
)
from apps.webhooks.views import (
    WebhookEndpointViewSet,
    WebhookDeliveryViewSet,
)
from apps.workflows.views import (
    WorkflowViewSet,
    WorkflowExecutionViewSet,
    WorkflowStepLogViewSet,
)
from apps.jobs.views import (
    JobViewSet,
)
from apps.ai.views import (
    AIProviderConfigViewSet,
    AIModelConfigViewSet,
    AICallLogViewSet,
)
from apps.agents.views import (
    AgentToolViewSet,
    AgentViewSet,
    AgentExecutionViewSet,
)
from apps.analytics.views import (
    AnalyticsEventViewSet,
    AnalyticsAggregationViewSet,
)
from apps.usage.views import (
    UsageRecordViewSet,
)
from apps.integrations.views import (
    IntegrationViewSet,
    IntegrationLogViewSet,
)
from apps.search.views import (
    SearchIndexViewSet,
)

# ─── Router ────────────────────────────────────────────────────────
router = DefaultRouter()

# Organizations
router.register(r"organizations", OrganizationViewSet)
router.register(r"memberships", MembershipViewSet)
router.register(r"invitations", InvitationViewSet)

# Billing
router.register(r"plans", PlanViewSet)
router.register(r"subscriptions", SubscriptionViewSet)
router.register(r"invoices", InvoiceViewSet)

# Quotas
router.register(r"quota-definitions", QuotaDefinitionViewSet)
router.register(r"quota-allocations", QuotaAllocationViewSet)

# Permissions
router.register(r"permissions", PermissionViewSet)
router.register(r"roles", RoleViewSet)
router.register(r"role-permissions", RolePermissionViewSet)

# Audit
router.register(r"audit-logs", AuditLogViewSet)

# Feature Flags
router.register(r"feature-flags", FeatureFlagViewSet)
router.register(r"feature-flag-assignments", FeatureFlagAssignmentViewSet)

# Settings
router.register(r"tenant-settings", TenantSettingViewSet)
router.register(r"global-settings", GlobalSettingViewSet)

# Users
router.register(r"users", UserViewSet)

# Notifications
router.register(r"notification-channels", NotificationChannelViewSet, basename="notification-channel")
router.register(r"notification-templates", NotificationTemplateViewSet, basename="notification-template")
router.register(r"notification-logs", NotificationLogViewSet, basename="notification-log")

# Storage
router.register(r"storage-backends", StorageBackendConfigViewSet, basename="storage-backend")
router.register(r"stored-objects", StoredObjectViewSet, basename="stored-object")

# Webhooks
router.register(r"webhook-endpoints", WebhookEndpointViewSet, basename="webhook-endpoint")
router.register(r"webhook-deliveries", WebhookDeliveryViewSet, basename="webhook-delivery")

# Workflows
router.register(r"workflows", WorkflowViewSet, basename="workflow")
router.register(r"workflow-executions", WorkflowExecutionViewSet, basename="workflow-execution")
router.register(r"workflow-step-logs", WorkflowStepLogViewSet, basename="workflow-step-log")

# Jobs
router.register(r"jobs", JobViewSet, basename="job")

# AI
router.register(r"ai-providers", AIProviderConfigViewSet, basename="ai-provider")
router.register(r"ai-models", AIModelConfigViewSet, basename="ai-model")
router.register(r"ai-call-logs", AICallLogViewSet, basename="ai-call-log")

# Agents
router.register(r"agent-tools", AgentToolViewSet, basename="agent-tool")
router.register(r"agents", AgentViewSet, basename="agent")
router.register(r"agent-executions", AgentExecutionViewSet, basename="agent-execution")

# Analytics
router.register(r"analytics-events", AnalyticsEventViewSet, basename="analytics-event")
router.register(r"analytics-aggregations", AnalyticsAggregationViewSet, basename="analytics-aggregation")

# Usage
router.register(r"usage-records", UsageRecordViewSet, basename="usage-record")

# Integrations
router.register(r"integrations", IntegrationViewSet, basename="integration")
router.register(r"integration-logs", IntegrationLogViewSet, basename="integration-log")

# Search
router.register(r"search-indices", SearchIndexViewSet, basename="search-index")

urlpatterns = router.urls

# ─── Company Radar (novos apps de dominio) ─────────────────────────
from django.urls import include, path

urlpatterns += [
    path("", include("apps.clients.urls")),
]
urlpatterns += [
    path("", include("apps.radar_templates.urls")),
]
urlpatterns += [
    path("", include("apps.radar_tasks.urls")),
]
urlpatterns += [
    path("", include("apps.radar_documents.urls")),
]
urlpatterns += [
    path("", include("apps.radar_calendar.urls")),
]
urlpatterns += [
    path("", include("apps.radar_reports.urls")),
]
urlpatterns += [
    path("", include("apps.radar_portal.urls")),
]
