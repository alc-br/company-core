from django.contrib import admin
from apps.billing.models import Plan, Subscription, Invoice


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_cents", "billing_cycle", "is_active", "display_order")
    list_filter = ("is_active", "billing_cycle")
    search_fields = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("organization", "plan", "status", "current_period_start", "current_period_end")
    list_filter = ("status",)
    search_fields = ("organization__name",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("organization", "amount_cents", "status", "due_date", "paid_at")
    list_filter = ("status",)
    search_fields = ("organization__name", "stripe_invoice_id")
