from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.webhooks.models import WebhookEndpoint, WebhookDelivery


app_name = "webhooks"


@login_required
def list_endpoints(request):
    endpoints = WebhookEndpoint.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "webhooks/endpoints.html", {"endpoints": endpoints})

@login_required
def list_deliveries(request):
    qs = WebhookDelivery.objects.filter(endpoint__organization=request.tenant) if request.tenant else WebhookDelivery.objects.none()
    deliveries = qs.order_by("-created_at")[:50]
    return render(request, "webhooks/deliveries.html", {"deliveries": deliveries})

