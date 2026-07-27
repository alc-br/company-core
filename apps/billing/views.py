from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.billing.models import Plan


app_name = "billing"


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

