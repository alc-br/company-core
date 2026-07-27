#!/usr/bin/env python3
"""Script to create views.py and urls.py for all modules that need them."""
import os

BASE = "/home/z/my-project/company-core"

# Module definitions: (module_name, models_to_import, views_content, url_routes)
modules = {
    "billing": {
        "imports": "from apps.billing.models import Plan",
        "views": '''
@login_required
def list_plans(request):
    plans = Plan.objects.filter(is_active=True).order_by("display_order", "price_cents")
    return render(request, "billing/plans.html", {"plans": plans})

@login_required
def list_subscriptions(request):
    if not request.tenant:
        return render(request, "billing/subscriptions.html", {"subscriptions": []})
    from apps.billing.models import Subscription
    subscriptions = Subscription.objects.filter(organization=request.tenant).order_by("-created_at")
    return render(request, "billing/subscriptions.html", {"subscriptions": subscriptions})
''',
        "urls": "path('', list_plans, name='plans'),\n    path('subscriptions/', list_subscriptions, name='subscriptions'),",
    },
    "ai": {
        "imports": "from apps.ai.models import AIProviderConfig, AICallLog",
        "views": '''
@login_required
def list_providers(request):
    providers = AIProviderConfig.objects.all()
    return render(request, "ai/providers.html", {"providers": providers})

@login_required
def call_logs(request):
    qs = AICallLog.objects.filter(organization=request.tenant) if request.tenant else AICallLog.objects.none()
    logs = qs.order_by("-created_at")[:50]
    return render(request, "ai/call_logs.html", {"logs": logs})
''',
        "urls": "path('providers/', list_providers, name='providers'),\n    path('logs/', call_logs, name='logs'),",
    },
    "agents": {
        "imports": "from apps.agents.models import Agent",
        "views": '''
@login_required
def list_agents(request):
    agents = Agent.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "agents/list.html", {"agents": agents})

@login_required
def detail_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    executions = agent.executions.order_by("-created_at")[:20]
    return render(request, "agents/detail.html", {"agent": agent, "executions": executions})
''',
        "urls": "path('', list_agents, name='list'),\n    path('<int:agent_id>/', detail_agent, name='detail'),",
        "extra_imports": "from django.shortcuts import get_object_or_404",
    },
    "audit": {
        "imports": "from apps.audit.models import AuditLog",
        "views": '''
@login_required
def list_logs(request):
    qs = AuditLog.objects.filter(organization=request.tenant) if request.tenant else AuditLog.objects.none()
    logs = qs.order_by("-created_at")[:100]
    return render(request, "audit/logs.html", {"logs": logs})
''',
        "urls": "path('', list_logs, name='logs'),",
    },
    "permissions": {
        "imports": "from apps.permissions.models import Permission, Role",
        "views": '''
@login_required
def list_permissions(request):
    permissions = Permission.objects.all()
    return render(request, "permissions/list.html", {"permissions": permissions})

@login_required
def list_roles(request):
    roles = Role.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "permissions/roles.html", {"roles": roles})
''',
        "urls": "path('', list_permissions, name='list'),\n    path('roles/', list_roles, name='roles'),",
    },
    "quotas": {
        "imports": "from apps.quotas.selectors import get_all_quotas",
        "views": '''
@login_required
def list_quotas(request):
    quotas = get_all_quotas(request.tenant.id) if request.tenant else []
    return render(request, "quotas/list.html", {"quotas": quotas})
''',
        "urls": "path('', list_quotas, name='list'),",
    },
    "feature_flags": {
        "imports": "from apps.feature_flags.models import FeatureFlag",
        "views": '''
@login_required
def list_flags(request):
    flags = FeatureFlag.objects.all()
    return render(request, "feature_flags/list.html", {"flags": flags})
''',
        "urls": "path('', list_flags, name='list'),",
    },
    "notifications": {
        "imports": "from apps.notifications.models import NotificationLog",
        "views": '''
@login_required
def list_notifications(request):
    qs = NotificationLog.objects.filter(channel__organization=request.tenant) if request.tenant else NotificationLog.objects.none()
    notifications = qs.order_by("-created_at")[:50]
    return render(request, "notifications/list.html", {"notifications": notifications})
''',
        "urls": "path('', list_notifications, name='list'),",
    },
    "settings": {
        "imports": "from apps.settings.models import TenantSetting",
        "views": '''
@login_required
def view_settings(request):
    if not request.tenant:
        return render(request, "settings/view.html", {"settings": []})
    settings_list = TenantSetting.objects.filter(organization=request.tenant)
    return render(request, "settings/view.html", {"settings": settings_list})
''',
        "urls": "path('', view_settings, name='view'),",
    },
    "webhooks": {
        "imports": "from apps.webhooks.models import WebhookEndpoint, WebhookDelivery",
        "views": '''
@login_required
def list_endpoints(request):
    endpoints = WebhookEndpoint.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "webhooks/endpoints.html", {"endpoints": endpoints})

@login_required
def list_deliveries(request):
    qs = WebhookDelivery.objects.filter(endpoint__organization=request.tenant) if request.tenant else WebhookDelivery.objects.none()
    deliveries = qs.order_by("-created_at")[:50]
    return render(request, "webhooks/deliveries.html", {"deliveries": deliveries})
''',
        "urls": "path('', list_endpoints, name='endpoints'),\n    path('deliveries/', list_deliveries, name='deliveries'),",
    },
    "workflows": {
        "imports": "from apps.workflows.models import Workflow",
        "views": '''
@login_required
def list_workflows(request):
    workflows = Workflow.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "workflows/list.html", {"workflows": workflows})
''',
        "urls": "path('', list_workflows, name='list'),",
    },
    "jobs": {
        "imports": "from apps.jobs.models import Job",
        "views": '''
@login_required
def list_jobs(request):
    qs = Job.objects.filter(organization=request.tenant) if request.tenant else Job.objects.none()
    jobs = qs.order_by("-created_at")[:50]
    return render(request, "jobs/list.html", {"jobs": jobs})
''',
        "urls": "path('', list_jobs, name='list'),",
    },
    "storage": {
        "imports": "from apps.storage.models import StoredObject",
        "views": '''
@login_required
def list_files(request):
    qs = StoredObject.objects.filter(organization=request.tenant) if request.tenant else StoredObject.objects.none()
    files = qs.order_by("-created_at")[:50]
    return render(request, "storage/list.html", {"files": files})
''',
        "urls": "path('', list_files, name='list'),",
    },
}

for mod_name, config in modules.items():
    mod_dir = os.path.join(BASE, "apps", mod_name)
    
    # Create views.py
    views_content = f"""from django.contrib.auth.decorators import login_required
from django.shortcuts import render
{config['imports']}
{config.get('extra_imports', '')}

app_name = "{mod_name}"

{config['views']}
"""
    views_path = os.path.join(mod_dir, "views.py")
    with open(views_path, "w") as f:
        f.write(views_content)
    
    # Create urls.py
    urls_content = f"""from django.urls import path
from apps.{mod_name}.views import *

app_name = "{mod_name}"

urlpatterns = [
    {config['urls']}
]
"""
    urls_path = os.path.join(mod_dir, "urls.py")
    with open(urls_path, "w") as f:
        f.write(urls_content)

print("All views and URLs created successfully!")
