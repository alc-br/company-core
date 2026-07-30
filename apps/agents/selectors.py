"""Selectors for agents app."""

from typing import Optional
from django.db.models import QuerySet
from apps.agents.models import Agent, AgentTool, AgentExecution


def get_agents(
    organization_id: Optional[int] = None,
    *,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> QuerySet[Agent]:
    """Return agents with optional filters.

    Args:
        organization_id: Filter by organization.
        is_active: Filter by active status.
        search: Search by agent name (case-insensitive).

    Returns:
        QuerySet of Agent objects with tools prefetched.
    """
    qs = Agent.objects.select_related("organization", "provider").prefetch_related("tools")
    if organization_id is not None:
        qs = qs.filter(organization_id=organization_id)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if search:
        qs = qs.filter(name__icontains=search)
    return qs


def get_agent_by_id(agent_id: int) -> Optional[Agent]:
    """Return a single agent by its ID, or None.

    Args:
        agent_id: Primary key of the agent.

    Returns:
        Agent instance with tools prefetched, or None.
    """
    return (
        Agent.objects
        .filter(id=agent_id)
        .select_related("organization", "provider")
        .prefetch_related("tools")
        .first()
    )


def get_agent_executions(
    *,
    agent_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    status: Optional[str] = None,
) -> QuerySet[AgentExecution]:
    """Return agent execution records with optional filters.

    Args:
        agent_id: Filter by agent.
        organization_id: Filter by organization (via agent).
        status: Filter by execution status.

    Returns:
        QuerySet of AgentExecution objects.
    """
    qs = AgentExecution.objects.select_related("agent", "agent__organization")
    if agent_id is not None:
        qs = qs.filter(agent_id=agent_id)
    if organization_id is not None:
        qs = qs.filter(agent__organization_id=organization_id)
    if status is not None:
        qs = qs.filter(status=status)
    return qs


# --- Existing queryset-based selectors preserved below ---

def get_agent_queryset(
    *,
    organization_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> QuerySet[Agent]:
    """Get agents queryset for API views."""
    queryset = Agent.objects.select_related("organization", "provider").prefetch_related("tools")

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if search:
        queryset = queryset.filter(name__icontains=search)

    return queryset


def get_agent_tool_queryset(
    *,
    search: Optional[str] = None,
) -> QuerySet[AgentTool]:
    """Get agent tools queryset for API views."""
    queryset = AgentTool.objects.all()

    if search:
        queryset = queryset.filter(name__icontains=search) | queryset.filter(code__icontains=search)

    return queryset


def get_agent_execution_queryset(
    *,
    agent_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    status: Optional[str] = None,
) -> QuerySet[AgentExecution]:
    """Get agent executions queryset for API views."""
    queryset = AgentExecution.objects.select_related("agent", "agent__organization")

    if agent_id is not None:
        queryset = queryset.filter(agent_id=agent_id)

    if organization_id is not None:
        queryset = queryset.filter(agent__organization_id=organization_id)

    if status is not None:
        queryset = queryset.filter(status=status)

    return queryset
