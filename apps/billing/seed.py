"""Catalogo de planos e criacao da assinatura inicial (trial) de uma organizacao.

Sem integracao com gateway de pagamento (Stripe) configurada neste ambiente —
o self-service de troca/cancelamento de plano so atualiza o registro local
da Subscription. Cobranca real fica fora do escopo até haver uma conta Stripe.
"""
from django.utils import timezone
from datetime import timedelta

from apps.billing.models import Plan, Subscription
from apps.common.constants import BillingCycle, SubscriptionStatus

TRIAL_DAYS = 14

PLAN_CATALOG = [
    {
        "name": "Inicial", "price_cents": 9700, "display_order": 1,
        "limits": {"maxClients": 20, "maxUsers": 3, "maxStorageMb": 1024},
        "features": {"list": [
            "Até 20 clientes", "3 usuários", "1 GB de armazenamento",
            "Templates básicos", "Suporte por e-mail",
        ], "highlight": False, "annualPriceCents": 97000},
    },
    {
        "name": "Profissional", "price_cents": 19700, "display_order": 2,
        "limits": {"maxClients": 100, "maxUsers": 10, "maxStorageMb": 5120},
        "features": {"list": [
            "Até 100 clientes", "10 usuários", "5 GB de armazenamento",
            "Templates avançados", "Portal do cliente", "Relatórios", "Suporte prioritário",
        ], "highlight": True, "annualPriceCents": 197000},
    },
    {
        "name": "Empresarial", "price_cents": 49700, "display_order": 3,
        "limits": {"maxClients": 500, "maxUsers": 50, "maxStorageMb": 25600},
        "features": {"list": [
            "Clientes ilimitados", "50 usuários", "25 GB de armazenamento",
            "Tudo do Profissional", "API de integração", "SLA garantido", "Gerente de sucesso",
        ], "highlight": False, "annualPriceCents": 497000},
    },
]


def ensure_plan_catalog():
    """Idempotente — cria os planos do catalogo se ainda nao existirem (por nome)."""
    for entry in PLAN_CATALOG:
        Plan.objects.update_or_create(
            name=entry["name"],
            defaults={
                "price_cents": entry["price_cents"],
                "display_order": entry["display_order"],
                "limits": entry["limits"],
                "features": entry["features"],
                "billing_cycle": BillingCycle.MONTHLY,
                "is_active": True,
            },
        )


def default_starter_plan():
    ensure_plan_catalog()
    return Plan.objects.filter(is_active=True).order_by("display_order").first()


def start_trial_subscription(organization, plan=None):
    """Cria a assinatura inicial em trial de 14 dias no plano informado (ou o de entrada)."""
    plan = plan or default_starter_plan()
    now = timezone.now()
    return Subscription.objects.create(
        organization=organization, plan=plan,
        status=SubscriptionStatus.TRIALING,
        current_period_start=now,
        current_period_end=now + timedelta(days=TRIAL_DAYS),
        trial_end=now + timedelta(days=TRIAL_DAYS),
    )
