from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.agents.models import Agent
from django.shortcuts import get_object_or_404

app_name = "agents"


@login_required
def list_agents(request):
    agents = Agent.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "agents/list.html", {"agents": agents})

@login_required
def detail_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    executions = agent.executions.order_by("-created_at")[:20]
    return render(request, "agents/detail.html", {"agent": agent, "executions": executions})

