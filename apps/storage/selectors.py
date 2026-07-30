from typing import Optional
from django.db.models import QuerySet
from apps.storage.models import StoredObject, StorageBackendConfig


def get_storage_backend_queryset(**kwargs) -> QuerySet[StorageBackendConfig]:
    """ViewSet-compatible queryset for StorageBackendConfig."""
    return get_storage_configs(**kwargs)


def get_stored_object_queryset(**kwargs) -> QuerySet[StoredObject]:
    """ViewSet-compatible queryset for StoredObject."""
    return get_stored_objects(**kwargs)


def get_stored_objects(
    organization_id: Optional[int] = None,
    *,
    content_type: Optional[str] = None,
    bucket: Optional[str] = None,
    limit: int = 100,
) -> QuerySet[StoredObject]:
    """Return stored objects with optional filters.

    Args:
        organization_id: Filter by organization.
        content_type: Filter by MIME content type.
        bucket: Filter by storage bucket name.
        limit: Maximum number of results.

    Returns:
        QuerySet of StoredObject objects.
    """
    qs = StoredObject.objects.select_related("organization", "uploaded_by")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if content_type:
        qs = qs.filter(content_type=content_type)
    if bucket:
        qs = qs.filter(bucket=bucket)
    return qs[:limit]


def get_storage_configs(
    organization_id: Optional[int] = None,
    *,
    is_default: Optional[bool] = None,
    backend_type: Optional[int] = None,
) -> QuerySet[StorageBackendConfig]:
    """Return storage backend configurations with optional filters.

    Args:
        organization_id: Filter by organization.
        is_default: Filter by whether config is the default.
        backend_type: Filter by backend type (integer from StorageBackendType).

    Returns:
        QuerySet of StorageBackendConfig objects.
    """
    qs = StorageBackendConfig.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if is_default is not None:
        qs = qs.filter(is_default=is_default)
    if backend_type is not None:
        qs = qs.filter(backend_type=backend_type)
    return qs


def get_organization_files(
    organization_id: int,
    *,
    limit: int = 100,
) -> QuerySet[StoredObject]:
    """Return stored files for a specific organization.

    Args:
        organization_id: Primary key of the organization.
        limit: Maximum number of results.

    Returns:
        QuerySet of StoredObject objects belonging to the organization, ordered by newest first.
    """
    return (
        StoredObject.objects
        .filter(organization_id=organization_id)
        .select_related("uploaded_by")
        .order_by("-created_at")[:limit]
    )
