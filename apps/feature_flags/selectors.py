from typing import Optional
from django.db.models import QuerySet
from apps.feature_flags.models import FeatureFlag, FeatureFlagAssignment


def get_all_flags(*, active_only=False, organization=None):
    """Return all feature flags, optionally filtered by active status and organization."""
    qs = FeatureFlag.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)
    if organization:
        qs = qs.filter(assignments__organization=organization, assignments__is_active=True).distinct()
    return qs.order_by('code')


def get_flag_by_code(code):
    """Return a single feature flag by its code, or None."""
    return FeatureFlag.objects.filter(code=code).first()


def get_flags_for_organization(organization_id):
    """Return active feature flags assigned to a specific organization."""
    return FeatureFlag.objects.filter(
        assignments__organization_id=organization_id,
        assignments__is_active=True,
        is_active=True
    ).distinct()


def get_flags_for_user(user_id):
    """Return active feature flags assigned to a specific user."""
    from django.db.models import Q
    return FeatureFlag.objects.filter(
        Q(users__id=user_id) | Q(assignments__user_id=user_id, assignments__is_active=True),
        is_active=True
    ).distinct()


def get_flag_assignments(flag_code):
    """Return all assignments for a given feature flag code."""
    return FeatureFlagAssignment.objects.filter(flag__code=flag_code).select_related('flag', 'organization', 'user')


# --- Existing queryset-based selectors preserved below ---

def get_feature_flag_queryset(
    *,
    is_active: Optional[bool] = None,
    code: Optional[str] = None,
) -> QuerySet[FeatureFlag]:
    """Get feature flags queryset for API views."""
    queryset = FeatureFlag.objects.select_related("created_by")

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if code is not None:
        queryset = queryset.filter(code=code)

    return queryset


def get_feature_flag_assignment_queryset(
    *,
    flag_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None,
    environment: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> QuerySet[FeatureFlagAssignment]:
    """Get feature flag assignments queryset for API views."""
    queryset = FeatureFlagAssignment.objects.select_related(
        "flag", "organization", "user"
    )

    if flag_id is not None:
        queryset = queryset.filter(flag_id=flag_id)

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)

    if environment is not None:
        queryset = queryset.filter(environment=environment)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset


def is_flag_active_for_organization(flag_code: str, organization_id: int) -> bool:
    """Check if a feature flag is active for a specific organization."""
    flag = FeatureFlag.objects.filter(code=flag_code).first()
    if not flag or not flag.is_active:
        return False

    assignment = FeatureFlagAssignment.objects.filter(
        flag=flag, organization_id=organization_id, is_active=True,
    ).first()
    return assignment is not None


def is_flag_active_for_user(flag_code: str, user_id: int) -> bool:
    """Check if a feature flag is active for a specific user."""
    flag = FeatureFlag.objects.filter(code=flag_code).first()
    if not flag or not flag.is_active:
        return False

    assignment = FeatureFlagAssignment.objects.filter(
        flag=flag, user_id=user_id, is_active=True,
    ).first()
    return assignment is not None
