import logging
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.billing.models import Plan, Subscription, Invoice
from apps.common.constants import BillingCycle
from apps.billing.serializers import (
    PlanSerializer,
    PlanListSerializer,
    SubscriptionSerializer,
    SubscriptionListSerializer,
    InvoiceSerializer,
)
from apps.billing.services import BillingService
from apps.billing.selectors import (
    get_plan_queryset,
    get_subscription_queryset,
    get_invoice_queryset,
)

logger = logging.getLogger(__name__)

app_name = "billing"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_plans(request):
    plans = Plan.objects.filter(is_active=True).order_by("display_order", "price_cents")
    return render(request, "billing/plans.html", {"plans": plans})


@login_required
def list_subscriptions(request):
    if not request.tenant:
        return render(request, "billing/subscriptions.html", {"subscriptions": []})
    subscriptions = Subscription.objects.filter(organization=request.tenant).order_by("-created_at")
    return render(request, "billing/subscriptions.html", {"subscriptions": subscriptions})


# ─── Plan CRUD Template Views (Admin Only) ──────────────────────────


class PlanForm(forms.ModelForm):
    features = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '{"feature": "valor"}'}),
        required=False,
        help_text="JSON com funcionalidades do plano"
    )
    limits = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '{"limite": "valor"}'}),
        required=False,
        help_text="JSON com limites do plano"
    )

    class Meta:
        model = Plan
        fields = ['name', 'stripe_price_id', 'description', 'price_cents', 'billing_cycle', 'is_active', 'display_order', 'features', 'limits']

    def clean_features(self):
        import json
        val = self.cleaned_data.get('features', '')
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                raise forms.ValidationError("JSON inválido para funcionalidades.")
        return {}

    def clean_limits(self):
        import json
        val = self.cleaned_data.get('limits', '')
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                raise forms.ValidationError("JSON inválido para limites.")
        return {}


@login_required
def create_plan(request):
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Plano criado com sucesso!")
            return redirect('billing:plans')
    else:
        form = PlanForm()
    return render(request, 'billing/plan_form.html', {'form': form})


@login_required
def edit_plan(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Plano atualizado com sucesso!")
            return redirect('billing:plans')
    else:
        form = PlanForm(instance=plan)
    return render(request, 'billing/plan_form.html', {'form': form, 'object': plan})


@login_required
def delete_plan(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, "Plano excluído com sucesso!")
        return redirect('billing:plans')
    return render(request, 'billing/plan_confirm_delete.html', {
        'object': plan,
        'cancel_url': reverse('billing:plans'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class PlanViewSet(viewsets.ModelViewSet):
    """ViewSet for Plan model. Admin-only for create/update/delete."""

    queryset = Plan.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "price_cents", "display_order", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return PlanListSerializer
        return PlanSerializer

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        return get_plan_queryset(
            is_active=is_active if is_active is not None else None,
        )

    def get_permissions(self):
        """Only admin users can create/update/delete plans."""
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        plan = BillingService.create_plan(**serializer.validated_data)
        serializer.instance = plan


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for Subscription model."""

    queryset = Subscription.objects.select_related("plan", "organization")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "status", "current_period_end"]

    def get_serializer_class(self):
        if self.action == "list":
            return SubscriptionListSerializer
        return SubscriptionSerializer

    def get_queryset(self):
        return get_subscription_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            status=self.request.query_params.get("status"),
        )

    def perform_create(self, serializer):
        subscription = BillingService.create_subscription(
            organization=serializer.validated_data["organization"],
            plan=serializer.validated_data["plan"],
            stripe_customer_id=serializer.validated_data.get("stripe_customer_id", ""),
            stripe_subscription_id=serializer.validated_data.get("stripe_subscription_id", ""),
        )
        serializer.instance = subscription

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Cancel a subscription."""
        subscription = self.get_object()
        at_period_end = request.data.get("at_period_end", True)
        try:
            canceled = BillingService.cancel_subscription(subscription, at_period_end=at_period_end)
            serializer = self.get_serializer(canceled)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def change_plan(self, request, pk=None):
        """Change the plan of a subscription."""
        subscription = self.get_object()
        plan_id = request.data.get("plan_id")
        if not plan_id:
            return Response(
                {"error": "plan_id field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            new_plan = Plan.objects.get(id=plan_id)
            updated = BillingService.change_plan(subscription, new_plan)
            serializer = self.get_serializer(updated)
            return Response(serializer.data)
        except Plan.DoesNotExist:
            return Response({"error": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice model (read-only for most users)."""

    queryset = Invoice.objects.select_related("organization", "subscription", "subscription__plan")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "due_date", "amount_cents", "status"]

    def get_queryset(self):
        return get_invoice_queryset(
            organization_id=self.request.query_params.get("organization_id"),
            subscription_id=self.request.query_params.get("subscription_id"),
            status=self.request.query_params.get("status"),
        )

    def get_serializer_class(self):
        return InvoiceSerializer

    def get_permissions(self):
        """Only admin users can create invoices."""
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        invoice = BillingService.create_invoice(
            organization=serializer.validated_data["organization"],
            subscription=serializer.validated_data["subscription"],
            amount_cents=serializer.validated_data["amount_cents"],
            stripe_invoice_id=serializer.validated_data.get("stripe_invoice_id", ""),
            due_date=serializer.validated_data.get("due_date"),
        )
        serializer.instance = invoice

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def mark_paid(self, request, pk=None):
        """Mark an invoice as paid."""
        invoice = self.get_object()
        try:
            paid = BillingService.mark_invoice_paid(invoice)
            serializer = self.get_serializer(paid)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─── Stripe Webhook View ──────────────────────────────────────────

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    """Handle incoming Stripe webhook events."""
    import json
    try:
        from apps.billing.stripe_service import StripeService
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        event = StripeService.construct_webhook_event(payload, sig_header)
        result = StripeService.handle_webhook_event(event)
        return JsonResponse({"status": "ok", "result": result})
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return JsonResponse({"error": str(e)}, status=400)
