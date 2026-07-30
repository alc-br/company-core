"""Selectors for workflows app."""

from typing import Optional
from django.db.models import QuerySet
from apps.workflows.models import Workflow, WorkflowExecution, WorkflowStepLog


def get_workflows(
    organization_id: Optional[int] = None,
    *,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> QuerySet[Workflow]:
    """Return workflows with optional filters.

    Args:
        organization_id: Filter by organization.
        is_active: Filter by active status.
        search: Search by workflow name (case-insensitive).

    Returns:
        QuerySet of Workflow objects.
    """
    qs = Workflow.objects.select_related("organization")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(name__icontains=search)
    return qs


def get_workflow_by_id(workflow_id: int) -> Optional[Workflow]:
    """Return a single workflow by its ID, or None.

    Args:
        workflow_id: Primary key of the workflow.

    Returns:
        Workflow instance or None.
    """
    return Workflow.objects.filter(id=workflow_id).select_related("organization").first()


def get_workflow_executions(
    *,
    workflow_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    status: Optional[int] = None,
) -> QuerySet[WorkflowExecution]:
    """Return workflow executions with optional filters.

    Args:
        workflow_id: Filter by workflow.
        organization_id: Filter by organization (via workflow).
        status: Filter by execution status (integer from WorkflowExecutionStatus).

    Returns:
        QuerySet of WorkflowExecution objects.
    """
    qs = WorkflowExecution.objects.select_related("workflow", "workflow__organization")
    if workflow_id is not None:
        qs = qs.filter(workflow_id=workflow_id)
    if organization_id is not None:
        qs = qs.filter(workflow__organization_id=organization_id)
    if status is not None:
        qs = qs.filter(status=status)
    return qs


# --- Existing queryset-based selectors preserved below ---

def get_workflow_queryset(
    *,
    organization_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> QuerySet[Workflow]:
    """Get workflows queryset for API views."""
    queryset = Workflow.objects.select_related("organization")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if search:
        queryset = queryset.filter(name__icontains=search)

    return queryset


def get_workflow_execution_queryset(
    *,
    workflow_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    status: Optional[int] = None,
) -> QuerySet[WorkflowExecution]:
    """Get workflow executions queryset for API views."""
    queryset = WorkflowExecution.objects.select_related("workflow", "workflow__organization")

    if workflow_id is not None:
        queryset = queryset.filter(workflow_id=workflow_id)

    if organization_id is not None:
        queryset = queryset.filter(workflow__organization_id=organization_id)

    if status is not None:
        queryset = queryset.filter(status=status)

    return queryset


def get_workflow_step_log_queryset(
    *,
    execution_id: Optional[int] = None,
    status: Optional[str] = None,
) -> QuerySet[WorkflowStepLog]:
    """Get workflow step logs queryset for API views."""
    queryset = WorkflowStepLog.objects.select_related("execution", "execution__workflow")

    if execution_id is not None:
        queryset = queryset.filter(execution_id=execution_id)

    if status is not None:
        queryset = queryset.filter(status=status)

    return queryset
