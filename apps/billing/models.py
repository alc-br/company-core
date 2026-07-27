from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.mixins import TimestampMixin
from apps.common.constants import BillingCycle, SubscriptionStatus


class Plan(TimestampMixin):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    stripe_price_id = models.CharField(max_length=255, blank=True, verbose_name=_("Stripe Price ID"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    features = models.JSONField(default=dict, blank=True, verbose_name=_("Funcionalidades"))
    limits = models.JSONField(default=dict, blank=True, verbose_name=_("Limites"))
    price_cents = models.PositiveIntegerField(default=0, verbose_name=_("Preço (centavos)"))
    billing_cycle = models.IntegerField(choices=BillingCycle.choices, default=BillingCycle.MONTHLY, verbose_name=_("Ciclo de Cobrança"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Ordem de Exibição"))

    class Meta:
        verbose_name = _("Plano")
        verbose_name_plural = _("Planos")
        ordering = ["display_order", "price_cents"]
        indexes = [models.Index(fields=["stripe_price_id"]), models.Index(fields=["is_active"])]

    def __str__(self):
        return self.name


class Subscription(TimestampMixin):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="subscriptions", verbose_name=_("Organização"))
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions", verbose_name=_("Plano"))
    stripe_subscription_id = models.CharField(max_length=255, blank=True, verbose_name=_("Stripe Subscription ID"))
    stripe_customer_id = models.CharField(max_length=255, blank=True, verbose_name=_("Stripe Customer ID"))
    status = models.IntegerField(choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE, verbose_name=_("Status"))
    current_period_start = models.DateTimeField(null=True, blank=True, verbose_name=_("Início do Período"))
    current_period_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Fim do Período"))
    cancel_at_period_end = models.BooleanField(default=False, verbose_name=_("Cancelar no fim do período"))
    trial_end = models.DateTimeField(null=True, blank=True, verbose_name=_("Fim do Teste"))

    class Meta:
        verbose_name = _("Assinatura")
        verbose_name_plural = _("Assinaturas")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["stripe_subscription_id"]),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.plan.name} ({self.get_status_display()})"


class Invoice(TimestampMixin):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="invoices", verbose_name=_("Organização"))
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices", verbose_name=_("Assinatura"))
    stripe_invoice_id = models.CharField(max_length=255, blank=True, verbose_name=_("Stripe Invoice ID"))
    amount_cents = models.PositiveIntegerField(verbose_name=_("Valor (centavos)"))
    status = models.CharField(max_length=50, default="pending", verbose_name=_("Status"))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Pago em"))
    due_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Data de Vencimento"))

    class Meta:
        verbose_name = _("Fatura")
        verbose_name_plural = _("Faturas")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invoice {self.stripe_invoice_id or self.id} - ${self.amount_cents / 100:.2f}"
