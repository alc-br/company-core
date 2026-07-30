from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.organizations.selectors import get_user_organizations
from apps.audit.models import AuditLog
from apps.ai.models import AICallLog
from django.utils import timezone


@login_required
def dashboard_view(request):
    """Main dashboard view showing overview statistics."""
    user_orgs = get_user_organizations(request.user.id)
    org_count = user_orgs.count()
    member_count = sum(org.memberships.count() for org in user_orgs)
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ai_calls_count = AICallLog.objects.filter(
        organization__in=user_orgs, created_at__gte=current_month,
    ).count()
    recent_logs = AuditLog.objects.filter(
        organization__in=user_orgs,
    ).order_by("-created_at")[:10]
    return render(request, "dashboard.html", {
        "user_orgs": user_orgs, "org_count": org_count,
        "member_count": member_count, "ai_calls_count": ai_calls_count,
        "recent_logs": recent_logs, "revenue": "0,00",
    })
