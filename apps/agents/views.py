"""DRF API ViewSets for agents app."""

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

from apps.agents.models import Agent, AgentTool, AgentExecution
from apps.agents.serializers import (
    AgentSerializer,
    AgentToolSerializer,
    AgentExecutionSerializer,
)
from apps.agents.selectors import (
    get_agent_queryset,
    get_agent_tool_queryset,
    get_agent_execution_queryset,
)

logger = logging.getLogger(__name__)

app_name = "agents"


# ─── Template Views ────────────────────────────────────────────────


@login_required
def list_agents(request):
    agents = Agent.objects.filter(organization=request.tenant).order_by('-created_at') if request.tenant else []
    return render(request, 'agents/list.html', {'agents': agents})


# ─── Agent CRUD ────────────────────────────────────────────────────


class AgentForm(forms.ModelForm):
    memory_config = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '{"max_messages": 10}'}),
        required=False,
        help_text="JSON com configuração de memória"
    )

    class Meta:
        model = Agent
        fields = ['name', 'description', 'system_prompt', 'provider', 'model_id', 'temperature', 'memory_config', 'is_active']

    def __init__(self, *args, **kwargs):
        org = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)
        if org:
            self.fields['provider'].queryset = self.fields['provider'].queryset.filter(organization=org)

    def clean_memory_config(self):
        import json
        val = self.cleaned_data.get('memory_config', '')
        if val:
            try:
                return json.loads(val)
            except json.JSONDecodeError:
                raise forms.ValidationError("JSON inválido para configuração de memória.")
        return {}


@login_required
def create_agent(request):
    if not request.tenant:
        messages.error(request, "Nenhuma organização selecionada.")
        return redirect('agents:list')
    if request.method == 'POST':
        form = AgentForm(request.POST, organization=request.tenant)
        if form.is_valid():
            agent = form.save(commit=False)
            agent.organization = request.tenant
            agent.save()
            messages.success(request, "Agente criado com sucesso!")
            return redirect('agents:list')
    else:
        form = AgentForm(organization=request.tenant)
    return render(request, 'agents/agent_form.html', {'form': form})


@login_required
def edit_agent(request, pk):
    agent = get_object_or_404(Agent, pk=pk)
    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent, organization=agent.organization)
        if form.is_valid():
            form.save()
            messages.success(request, "Agente atualizado com sucesso!")
            return redirect('agents:list')
    else:
        form = AgentForm(instance=agent, organization=agent.organization)
    return render(request, 'agents/agent_form.html', {'form': form, 'object': agent})


@login_required
def delete_agent(request, pk):
    agent = get_object_or_404(Agent, pk=pk)
    if request.method == 'POST':
        agent.delete()
        messages.success(request, "Agente excluído com sucesso!")
        return redirect('agents:list')
    return render(request, 'agents/agent_confirm_delete.html', {
        'object': agent,
        'cancel_url': reverse('agents:list'),
    })


# ─── DRF API ViewSets ───────────────────────────────────────────────


class AgentToolViewSet(viewsets.ModelViewSet):
    """ViewSet for AgentTool model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "created_at"]

    def get_serializer_class(self):
        return AgentToolSerializer

    def get_queryset(self):
        return get_agent_tool_queryset(
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        serializer.save()


class AgentViewSet(viewsets.ModelViewSet):
    """ViewSet for Agent model."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "is_active", "created_at"]

    def get_serializer_class(self):
        return AgentSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        if not org_id:
            org_id = self.request.query_params.get("organization_id")
        return get_agent_queryset(
            organization_id=org_id,
            is_active=self.request.query_params.get("is_active", type=str),
            search=self.request.query_params.get("search"),
        )

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def toggle_active(self, request, pk=None):
        """Toggle the active status of an agent."""
        agent = self.get_object()
        agent.is_active = not agent.is_active
        agent.save(update_fields=["is_active"])
        serializer = self.get_serializer(agent)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def execute(self, request, pk=None):
        """Trigger an agent execution."""
        agent = self.get_object()
        input_data = request.data.get("input_data", {})
        try:
            execution = AgentExecution.objects.create(
                agent=agent,
                input_data=input_data,
            )
            serializer = AgentExecutionSerializer(execution)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Agent execution creation failed")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AgentExecution model (read-only)."""

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["-created_at", "status", "duration_ms"]

    def get_serializer_class(self):
        return AgentExecutionSerializer

    def get_queryset(self):
        org_id = getattr(self.request, "tenant", None)
        return get_agent_execution_queryset(
            agent_id=self.request.query_params.get("agent_id", type=int),
            organization_id=org_id,
            status=self.request.query_params.get("status"),
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """Get agent execution statistics."""
        qs = self.get_queryset()
        from django.db.models import Count, Avg, Sum
        stats = qs.aggregate(
            total_executions=Count("id"),
            avg_tokens_used=Avg("tokens_used"),
            avg_duration_ms=Avg("duration_ms"),
            total_tokens_used=Sum("tokens_used"),
        )
        return Response({"stats": stats})
