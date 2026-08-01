"""Endpoints /api/v1/plans e /api/v1/invoices consumidos por /app/assinatura.

A assinatura em si (GET/PUT) fica em CurrentOrganizationView
(apps/organizations/team_views.py), pois o frontend busca tudo junto via
/api/organizations?include=subscription.
"""
import re

from rest_framework.response import Response

from apps.clients.views import TenantAPIView
from apps.billing.models import Plan, Invoice
from apps.billing.seed import ensure_plan_catalog


def _slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def serialize_plan(plan, current_plan_id=None):
    features = plan.features or {}
    return {
        "id": plan.id,
        "name": plan.name,
        "slug": _slugify(plan.name),
        "price": plan.price_cents / 100,
        "annual_price": (features.get("annualPriceCents") / 100) if features.get("annualPriceCents") else None,
        "max_clients": (plan.limits or {}).get("maxClients", 0),
        "max_users": (plan.limits or {}).get("maxUsers", 0),
        "max_storage_mb": (plan.limits or {}).get("maxStorageMb", 0),
        "features": features.get("list", []),
        "highlight": bool(features.get("highlight")),
        "is_current": plan.id == current_plan_id,
    }


class PlanListView(TenantAPIView):
    def get(self, request):
        ensure_plan_catalog()
        plans = Plan.objects.filter(is_active=True).order_by("display_order")
        return Response([serialize_plan(p) for p in plans])


class InvoiceListView(TenantAPIView):
    def get(self, request):
        invoices = Invoice.objects.filter(organization=request.tenant).order_by("-created_at")[:50]
        return Response([
            {
                "id": inv.id,
                "date": inv.paid_at or inv.due_date or inv.created_at,
                "amount": inv.amount_cents / 100,
                "status": inv.status,
            }
            for inv in invoices
        ])
