"""Selectors for AI app."""

from typing import Optional
from django.db.models import QuerySet
from apps.ai.models import AIProviderConfig, AIModelConfig, AICallLog


def get_provider_configs(
    organization_id: Optional[int] = None,
    *,
    provider_name: Optional[int] = None,
    is_default: Optional[bool] = None,
) -> QuerySet[AIProviderConfig]:
    """Return AI provider configurations with optional filters.

    Args:
        organization_id: Filter by organization.
        provider_name: Filter by provider name (integer from AIProvider).
        is_default: Filter by whether config is the default.

    Returns:
        QuerySet of AIProviderConfig objects.
    """
    qs = AIProviderConfig.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if provider_name is not None:
        qs = qs.filter(provider_name=provider_name)
    if is_default is not None:
        qs = qs.filter(is_default=is_default)
    return qs


def get_model_configs(
    provider_id: Optional[int] = None,
    *,
    search: Optional[str] = None,
) -> QuerySet[AIModelConfig]:
    """Return AI model configurations with optional filters.

    Args:
        provider_id: Filter by provider config.
        search: Search by model ID or display name (case-insensitive).

    Returns:
        QuerySet of AIModelConfig objects.
    """
    qs = AIModelConfig.objects.select_related("provider")
    if provider_id is not None:
        qs = qs.filter(provider_id=provider_id)
    if search:
        qs = qs.filter(model_id__icontains=search) | qs.filter(display_name__icontains=search)
    return qs


def get_call_logs(
    organization_id: Optional[int] = None,
    *,
    user_id: Optional[int] = None,
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
) -> QuerySet[AICallLog]:
    """Return AI call log records with optional filters.

    Args:
        organization_id: Filter by organization.
        user_id: Filter by user.
        provider_name: Filter by provider name (string).
        model: Filter by model name.

    Returns:
        QuerySet of AICallLog objects.
    """
    qs = AICallLog.objects.select_related("organization", "user")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if user_id is not None:
        qs = qs.filter(user_id=user_id)
    if provider_name:
        qs = qs.filter(provider_name=provider_name)
    if model:
        qs = qs.filter(model=model)
    return qs


# --- Existing queryset-based selectors preserved below ---

def get_ai_provider_queryset(
    *,
    organization_id: Optional[int] = None,
    provider_name: Optional[int] = None,
    is_default: Optional[bool] = None,
) -> QuerySet[AIProviderConfig]:
    """Get AI provider configs queryset for API views."""
    queryset = AIProviderConfig.objects.select_related("organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if provider_name is not None:
        queryset = queryset.filter(provider_name=provider_name)

    if is_default is not None:
        queryset = queryset.filter(is_default=is_default)

    return queryset


def get_ai_model_config_queryset(
    *,
    provider_id: Optional[int] = None,
    search: Optional[str] = None,
) -> QuerySet[AIModelConfig]:
    """Get AI model configs queryset for API views."""
    queryset = AIModelConfig.objects.select_related("provider")

    if provider_id is not None:
        queryset = queryset.filter(provider_id=provider_id)

    if search:
        queryset = queryset.filter(
            model_id__icontains=search
        ) | queryset.filter(display_name__icontains=search)

    return queryset


def get_ai_call_log_queryset(
    *,
    organization_id: Optional[int] = None,
    user_id: Optional[int] = None,
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
) -> QuerySet[AICallLog]:
    """Get AI call logs queryset for API views."""
    queryset = AICallLog.objects.select_related("organization", "user")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if user_id is not None:
        queryset = queryset.filter(user_id=user_id)

    if provider_name:
        queryset = queryset.filter(provider_name=provider_name)

    if model:
        queryset = queryset.filter(model=model)

    return queryset
