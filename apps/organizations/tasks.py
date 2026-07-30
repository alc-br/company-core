from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def cleanup_expired_invitations():
    """Mark expired invitations as expired."""
    from apps.organizations.models import Invitation
    Invitation.objects.filter(
        status=1,  # PENDING
        expires_at__lt=timezone.now(),
    ).update(status=4, updated_at=timezone.now())  # EXPIRED


@shared_task
def send_invitation_reminder(invitation_id):
    """Send reminder for pending invitation."""
    from apps.organizations.models import Invitation
    try:
        invitation = Invitation.objects.get(id=invitation_id, status=1)
    except Invitation.DoesNotExist:
        return None
    # TODO: trigger email via NotificationService
    return {"invitation_id": invitation_id, "sent_at": timezone.now().isoformat()}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def cleanup_expired_invitations_task(self):
    """Mark expired invitations."""
    from apps.organizations.models import Invitation

    try:
        count = Invitation.objects.filter(
            status=1,  # PENDING
            expires_at__lt=timezone.now(),
        ).update(status=4, updated_at=timezone.now())  # EXPIRED
        return {"expired_count": count}
    except Exception as exc:
        self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_org_stats_task(self, organization_id):
    """Generate organization statistics."""
    from apps.organizations.models import Organization, Membership, Invitation
    from django.db.models import Count, Q

    try:
        org = Organization.objects.get(id=organization_id)

        active_members = Membership.objects.filter(
            organization=org, status=1  # ACTIVE
        ).count()

        pending_invitations = Invitation.objects.filter(
            organization=org, status=1  # PENDING
        ).count()

        members_by_role = dict(
            Membership.objects.filter(
                organization=org, status=1
            ).values_list("role", flat=True).annotate(
                count=Count("id")
            ).values_list("role", "count")
        )

        stats = {
            "organization_id": organization_id,
            "organization_name": org.name,
            "active_members": active_members,
            "pending_invitations": pending_invitations,
            "members_by_role": members_by_role,
            "created_at": org.created_at.isoformat() if org.created_at else None,
        }

        return stats
    except Organization.DoesNotExist:
        return None
    except Exception as exc:
        self.retry(exc=exc)
