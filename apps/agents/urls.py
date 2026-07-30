"""URL configuration for agents app."""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.agents.views import (
    list_agents,
    create_agent,
    edit_agent,
    delete_agent,
    AgentToolViewSet,
    AgentViewSet,
    AgentExecutionViewSet,
)

app_name = "agents"

# Template URLs
urlpatterns = [
    path('', list_agents, name='list'),
    path('create/', create_agent, name='create'),
    path('<int:pk>/edit/', edit_agent, name='edit'),
    path('<int:pk>/delete/', delete_agent, name='delete'),
]

# DRF API router URLs
router = DefaultRouter()
router.register(r'api/tools', AgentToolViewSet, basename='api-agent-tool')
router.register(r'api/agents', AgentViewSet, basename='api-agent')
router.register(r'api/executions', AgentExecutionViewSet, basename='api-agent-execution')

urlpatterns += router.urls
