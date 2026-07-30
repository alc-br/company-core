"""Selectors for jobs app."""

from typing import Optional
from django.db.models import QuerySet
from apps.jobs.models import Job
from apps.common.constants import JobStatus


def get_jobs(
    organization_id: Optional[int] = None,
    *,
    status: Optional[int] = None,
    priority: Optional[int] = None,
    task_path: Optional[str] = None,
) -> QuerySet[Job]:
    """Return jobs with optional filters.

    Args:
        organization_id: Filter by organization.
        status: Filter by job status (integer from JobStatus).
        priority: Filter by priority level.
        task_path: Filter by task path.

    Returns:
        QuerySet of Job objects.
    """
    qs = Job.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if status is not None:
        qs = qs.filter(status=status)
    if priority is not None:
        qs = qs.filter(priority=priority)
    if task_path:
        qs = qs.filter(task_path=task_path)
    return qs


def get_job_by_id(job_id: int) -> Optional[Job]:
    """Return a single job by its ID, or None.

    Args:
        job_id: Primary key of the job.

    Returns:
        Job instance or None.
    """
    return Job.objects.filter(id=job_id).select_related("organization").first()


def get_pending_jobs(organization_id: Optional[int] = None, *, limit: int = 100) -> QuerySet[Job]:
    """Return pending jobs, optionally filtered by organization.

    Args:
        organization_id: Filter by organization.
        limit: Maximum number of results.

    Returns:
        QuerySet of pending Job objects ordered by priority (highest first).
    """
    qs = Job.objects.filter(status=JobStatus.PENDING).order_by("-priority", "created_at")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    return qs[:limit]


# --- Existing queryset-based selectors preserved below ---

def get_job_queryset(
    *,
    organization_id: Optional[int] = None,
    status: Optional[int] = None,
    priority: Optional[int] = None,
    task_path: Optional[str] = None,
) -> QuerySet[Job]:
    """Get jobs queryset for API views."""
    queryset = Job.objects.select_related("organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if status is not None:
        queryset = queryset.filter(status=status)

    if priority is not None:
        queryset = queryset.filter(priority=priority)

    if task_path:
        queryset = queryset.filter(task_path=task_path)

    return queryset
