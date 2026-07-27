from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.notifications.models import NotificationLog


app_name = "notifications"


@login_required
def list_notifications(request):
    qs = NotificationLog.objects.filter(channel__organization=request.tenant) if request.tenant else NotificationLog.objects.none()
    notifications = qs.order_by("-created_at")[:50]
    return render(request, "notifications/list.html", {"notifications": notifications})

