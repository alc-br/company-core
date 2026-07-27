from django.urls import path
from apps.agents import views as agents_views

app_name = "agents"

urlpatterns = [
    path('', agents_views.list_agents, name='list'),
    path('<int:agent_id>/', agents_views.detail_agent, name='detail'),
]
