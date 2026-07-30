"""Selectors for search app."""

from typing import Optional
from django.db.models import QuerySet
from apps.search.models import SearchIndex


def get_search_indices(
    content_type: Optional[str] = None,
    *,
    search: Optional[str] = None,
) -> QuerySet[SearchIndex]:
    """Return search index entries with optional filters.

    Args:
        content_type: Filter by content type.
        search: Filter by searching content (case-insensitive contains).

    Returns:
        QuerySet of SearchIndex objects.
    """
    qs = SearchIndex.objects.all()
    if content_type:
        qs = qs.filter(content_type=content_type)
    if search:
        qs = qs.filter(content__icontains=search)
    return qs


def get_recent_searches(limit: int = 50) -> QuerySet[SearchIndex]:
    """Return the most recently indexed entries.

    Args:
        limit: Maximum number of results.

    Returns:
        QuerySet of SearchIndex objects ordered by most recent indexed_at.
    """
    return SearchIndex.objects.order_by("-indexed_at")[:limit]


# --- Existing queryset-based selectors preserved below ---

def get_search_index_queryset(
    *,
    content_type: Optional[str] = None,
    search: Optional[str] = None,
) -> QuerySet[SearchIndex]:
    """Get search index queryset for API views."""
    queryset = SearchIndex.objects.all()

    if content_type:
        queryset = queryset.filter(content_type=content_type)

    if search:
        queryset = queryset.filter(content__icontains=search)

    return queryset
