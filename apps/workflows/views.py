"""DRF API ViewSets for workflows app."""

import logging
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.workflows.models import Workflow, WorkflowExecution, WorkflowStepLog
from apps.workflows.serializers import (
    WorkflowSerializer,
    WorkflowExecutionSerializer,
    WorkflowStepLogSerializer,
)
from apps.workflows.selectors import (
    get_workflow_queryset,
    get_workflow_execution_queryset,
    get_workflow_step_log_queryset,
)

logger = logging.getLogger(__name__)

app_name = "workflows"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_workflows(request):
    workflows = Workflow.objects.filter(organization=request.tenant).order_by('-created_at') if request.tenant else []
    return render(request, 'workflows/list.html', {'workflows': workflows})


# ─── Workflow CRUD ─────────────────────────────────────────────────


class WorkflowForm(forms.ModelForm):
    steps_config = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': '[{"step": "name", "action": "type"}]}'}),
        required=False,
        help_text="JSON com a configuração das etapas"
    )

    class Meta:
        model = Workflow
        fields = ['name', 'description', 'steps_config', 'is_active']

    def clean_steps_config(self):
        import json
        val = self.cleaned_data.get('steps_config', '')
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                raise forms.ValidationError("JSON inválido para etapas.")
        return []


@login_required
def create_workflow(request):
    if not request.tenant:
        messages.error(request, "Nenhuma organização selecionada.")
        return redirect('workflows:list')
    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save(commit=False)
            workflow.organization = request.tenant
            workflow.save()
            messages.success(request, "Workflow criado com sucesso!")
            return redirect('workflows:list')
    else:
        form = WorkflowForm()
    return render(request, 'workflows/workflow_form.html', {'form': form})


@login_required
def edit_workflow(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    if request.method == 'POST':
        form = WorkflowForm(request.POST, instance=workflow)
        if form.is_valid():
            form.save()
            messages.success(request, "Workflow atualizado com sucesso!")
            return redirect('workflows:list')
    else:
        form = WorkflowForm(instance=workflow)
    return render(request, 'workflows/workflow_form.html', {'form': form, 'object': workflow})


@login_required
def delete_workflow(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    if request.method == 'POST':
        workflow.delete()
        messages.success(request, "Workflow excluído com sucesso!")
        return redirect('workflows:list')
    return render(request, 'workflows/workflow_confirm_delete.html', {
        'object': workflow,
        'cancel_url': reverse('workflows:list'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class WorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for Workflow model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "is_active", "created_at"]

    def get_serializer_class(self):
        return WorkflowSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_workflow_queryset(
            organization_id=org_id,
            is_active=self.request.query_params.get("is_active", type=str),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def execute(self, request, pk=None):
        """Trigger execution of this workflow."""
        workflow = self.get_object()
        input_data = request.data.get("input_data", {})
        try:
            execution = WorkflowExecution.objects.create(
                workflow=workflow,
                input_data=input_data,
            )
            serializer = WorkflowExecutionSerializer(execution)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Workflow execution creation failed")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of a workflow."""
        workflow = self.get_object()
        workflow.is_active = not workflow.is_active
        workflow.save(update_fields=["is_active"])
        serializer = self.get_serializer(workflow)
        return Response(serializer.data)


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for WorkflowExecution model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-created_at", "status", "started_at"]

    def get_serializer_class(self):
        return WorkflowExecutionSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        return get_workflow_execution_queryset(
            workflow_id=self.request.query_params.get("workflow_id", type=int),
            organization_id=org_id,
            status=self.request.query_params.get("status", type=int),
        )

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def step_logs(self, request, pk=None):
        """Get step logs for this execution."""
        execution = self.get_object()
        logs = get_workflow_step_log_queryset(execution_id=execution.id)
        serializer = WorkflowStepLogSerializer(logs, many=True)
        return Response(serializer.data)


class WorkflowStepLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for WorkflowStepLog model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "step_name", "duration_ms"]

    def get_serializer_class(self):
        return WorkflowStepLogSerializer

    def get_queryset(self):
        return get_workflow_step_log_queryset(
            execution_id=self.request.query_params.get("execution_id", type=int),
            status=self.request.query_params.get("status"),
        )
