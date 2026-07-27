import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.organizations.models import Organization, Membership

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Organization)
def on_organization_created(sender, instance, created, **kwargs):
    """Log when a new organization is created."""
    if created:
        logger.info(f"New organization created: {instance.name} (id={instance.id})")


@receiver(post_save, sender=Membership)
def on_membership_created(sender, instance, created, **kwargs):
    """Log when a new membership is created."""
    if created:
        logger.info(
            f"New membership: user={instance.user_id}, "
            f"org={instance.organization_id}, role={instance.role}"
        )


@receiver(post_delete, sender=Membership)
def on_membership_deleted(sender, instance, **kwargs):
    """Log when a membership is deleted."""
    logger.info(
        f"Membership deleted: user={instance.user_id}, "
        f"org={instance.organization_id}"
    )
