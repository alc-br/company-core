#!/usr/bin/env python3
"""Write correct urls.py for all modules."""
import os

BASE = "/home/z/my-project/company-core"

urls = {
    "organizations": {
        "file": """from django.urls import path
from apps.organizations import views as org_views

app_name = "organizations"

urlpatterns = [
    path('', org_views.list_organizations, name='list'),
    path('create/', org_views.create_organization, name='create'),
    path('<int:org_id>/', org_views.detail_organization, name='detail'),
    path('switch/', org_views.switch_organization, name='switch'),
    path('invite/', org_views.invite_member, name='invite'),
]
"""
    },
    "billing": {
        "file": """from django.urls import path
from apps.billing import views as billing_views

app_name = "billing"

urlpatterns = [
    path('', billing_views.list_plans, name='plans'),
    path('subscriptions/', billing_views.list_subscriptions, name='subscriptions'),
]
"""
    },
    "ai": {
        "file": """from django.urls import path
from apps.ai import views as ai_views

app_name = "ai"

urlpatterns = [
    path('providers/', ai_views.list_providers, name='providers'),
    path('logs/', ai_views.call_logs, name='logs'),
]
"""
    },
    "agents": {
        "file": """from django.urls import path
from apps.agents import views as agents_views

app_name = "agents"

urlpatterns = [
    path('', agents_views.list_agents, name='list'),
    path('<int:agent_id>/', agents_views.detail_agent, name='detail'),
]
"""
    },
    "audit": {
        "file": """from django.urls import path
from apps.audit import views as audit_views

app_name = "audit"

urlpatterns = [
    path('', audit_views.list_logs, name='logs'),
]
"""
    },
    "permissions": {
        "file": """from django.urls import path
from apps.permissions import views as perm_views

app_name = "permissions"

urlpatterns = [
    path('', perm_views.list_permissions, name='list'),
    path('roles/', perm_views.list_roles, name='roles'),
]
"""
    },
    "quotas": {
        "file": """from django.urls import path
from apps.quotas import views as quota_views

app_name = "quotas"

urlpatterns = [
    path('', quota_views.list_quotas, name='list'),
]
"""
    },
    "feature_flags": {
        "file": """from django.urls import path
from apps.feature_flags import views as ff_views

app_name = "feature_flags"

urlpatterns = [
    path('', ff_views.list_flags, name='list'),
]
"""
    },
    "notifications": {
        "file": """from django.urls import path
from apps.notifications import views as notif_views

app_name = "notifications"

urlpatterns = [
    path('', notif_views.list_notifications, name='list'),
]
"""
    },
    "settings": {
        "file": """from django.urls import path
from apps.settings import views as settings_views

app_name = "settings"

urlpatterns = [
    path('', settings_views.view_settings, name='view'),
]
"""
    },
    "webhooks": {
        "file": """from django.urls import path
from apps.webhooks import views as wh_views

app_name = "webhooks"

urlpatterns = [
    path('', wh_views.list_endpoints, name='endpoints'),
    path('deliveries/', wh_views.list_deliveries, name='deliveries'),
]
"""
    },
    "workflows": {
        "file": """from django.urls import path
from apps.workflows import views as wf_views

app_name = "workflows"

urlpatterns = [
    path('', wf_views.list_workflows, name='list'),
]
"""
    },
    "jobs": {
        "file": """from django.urls import path
from apps.jobs import views as job_views

app_name = "jobs"

urlpatterns = [
    path('', job_views.list_jobs, name='list'),
]
"""
    },
    "storage": {
        "file": """from django.urls import path
from apps.storage import views as storage_views

app_name = "storage"

urlpatterns = [
    path('', storage_views.list_files, name='list'),
]
"""
    },
}

for mod_name, config in urls.items():
    path = os.path.join(BASE, "apps", mod_name, "urls.py")
    with open(path, "w") as f:
        f.write(config["file"])

print("All URLs written correctly!")
