from django.urls import path
from apps.workflows import views as wf_views

app_name = "workflows"

urlpatterns = [
    path('', wf_views.list_workflows, name='list'),
]
