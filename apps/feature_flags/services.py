import logging
from django.db import transaction
from apps.common.exceptions import NotFoundException, ServiceException

logger = logging.getLogger(__name__)


class FeatureFlagService:
    @staticmethod
    def is_active(code, user=None, organization=None, environment=None):
        """Check if a feature flag is active for the given context."""
        from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment
        from django.db.models import Q

        try:
            flag = FeatureFlag.objects.get(code=code)
        except FeatureFlag.DoesNotExist:
            return False

        if not flag.is_active:
            return False

        # Check M2M users
        if user and user in flag.users.all():
            return True

        # Check M2M groups
        if user and flag.groups.filter(id__in=user.groups.all()).exists():
            return True

        # Check assignments
        filters = Q(flag=flag, is_active=True)
        if organization:
            filters &= Q(organization=organization)
        if user:
            filters &= (Q(user=user) | Q(user__isnull=True))
        if environment:
            filters &= Q(environment=environment)
        else:
            filters &= Q(environment='production')

        return FeatureFlagAssignment.objects.filter(filters).exists()

    @staticmethod
    def enable(code):
        """Enable a feature flag by its code."""
        from apps.feature_flags.models import FeatureFlag
        flag = FeatureFlag.objects.filter(code=code).first()
        if not flag:
            raise NotFoundException(f"Feature flag '{code}' not found")
        flag.is_active = True
        flag.save(update_fields=['is_active'])
        return flag

    @staticmethod
    def disable(code):
        """Disable a feature flag by its code."""
        from apps.feature_flags.models import FeatureFlag
        flag = FeatureFlag.objects.filter(code=code).first()
        if not flag:
            raise NotFoundException(f"Feature flag '{code}' not found")
        flag.is_active = False
        flag.save(update_fields=['is_active'])
        return flag

    @staticmethod
    @transaction.atomic
    def create_flag(code, name, description="", created_by=None, is_active=False):
        """Create a new feature flag."""
        from apps.feature_flags.models import FeatureFlag
        flag = FeatureFlag.objects.create(
            code=code,
            name=name,
            description=description,
            created_by=created_by,
            is_active=is_active,
        )
        logger.info(f"Feature flag '{code}' created (id={flag.id})")
        return flag

    @staticmethod
    @transaction.atomic
    def update_flag(flag, name=None, description=None, is_active=None):
        """Update an existing feature flag."""
        if name is not None:
            flag.name = name
        if description is not None:
            flag.description = description
        if is_active is not None:
            flag.is_active = is_active
        flag.save(update_fields=[f for f in ('name', 'description', 'is_active', 'updated_at') if getattr(flag, f, None) is not None or f == 'updated_at'])
        logger.info(f"Feature flag '{flag.code}' updated")
        return flag

    @staticmethod
    @transaction.atomic
    def toggle_flag(flag):
        """Toggle a feature flag's active state."""
        flag.is_active = not flag.is_active
        flag.save(update_fields=['is_active', 'updated_at'])
        logger.info(f"Feature flag '{flag.code}' toggled to {'active' if flag.is_active else 'inactive'}")
        return flag

    @staticmethod
    @transaction.atomic
    def assign_flag_to_organization(flag, organization, environment="production", is_active=True):
        """Assign a feature flag to an organization (accepts flag object)."""
        from apps.feature_flags.models import FeatureFlagAssignment
        assignment, created = FeatureFlagAssignment.objects.update_or_create(
            flag=flag, organization=organization, user=None,
            defaults={'is_active': is_active, 'environment': environment}
        )
        return assignment

    @staticmethod
    @transaction.atomic
    def assign_flag_to_user(flag, user, environment="production", is_active=True):
        """Assign a feature flag to a user (accepts flag object)."""
        from apps.feature_flags.models import FeatureFlagAssignment
        assignment, created = FeatureFlagAssignment.objects.update_or_create(
            flag=flag, user=user, organization=None,
            defaults={'is_active': is_active, 'environment': environment}
        )
        return assignment

    @staticmethod
    @transaction.atomic
    def assign_to_organization(code, organization, is_active=True):
        """Assign a feature flag to an organization."""
        from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment
        flag = FeatureFlag.objects.get(code=code)
        assignment, created = FeatureFlagAssignment.objects.update_or_create(
            flag=flag, organization=organization, user=None,
            defaults={'is_active': is_active, 'environment': 'production'}
        )
        return assignment

    @staticmethod
    def assign_to_user(code, user, is_active=True):
        """Assign a feature flag to a user."""
        from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment
        flag = FeatureFlag.objects.get(code=code)
        assignment, created = FeatureFlagAssignment.objects.update_or_create(
            flag=flag, user=user, organization=None,
            defaults={'is_active': is_active, 'environment': 'production'}
        )
        return assignment
