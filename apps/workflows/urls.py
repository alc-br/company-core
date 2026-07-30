"""URL configuration for workflows app."""

from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.workflows.views import (
    list_workflows,
    create_workflow,
    edit_workflow,
    delete_workflow,
    WorkflowViewSet,
    WorkflowExecutionViewSet,
    WorkflowStepLogViewSet,
)

app_name = "workflows"

# Template URLs
urlpatterns = [
    path('', list_workflows, name='list'),
    path('create/', create_workflow, name='create'),
    path('<int:pk>/edit/', edit_workflow, name='edit'),
    path('<int:pk>/delete/', delete_workflow, name='delete'),
]

# DRF API router URLs
router = DefaultRouter()
router.register(r'api/workflows', WorkflowViewSet, basename='api-workflow')
router.register(r'api/executions', WorkflowExecutionViewSet, basename='api-workflow-execution')
router.register(r'api/step-logs', WorkflowStepLogViewSet, basename='api-workflow-step-log')

urlpatterns += router.urls
