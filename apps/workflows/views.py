from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.workflows.models import Workflow


app_name = "workflows"


@login_required
def list_workflows(request):
    workflows = Workflow.objects.filter(organization=request.tenant) if request.tenant else []
    return render(request, "workflows/list.html", {"workflows": workflows})

