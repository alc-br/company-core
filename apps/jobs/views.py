from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.jobs.models import Job


app_name = "jobs"


@login_required
def list_jobs(request):
    qs = Job.objects.filter(organization=request.tenant) if request.tenant else Job.objects.none()
    jobs = qs.order_by("-created_at")[:50]
    return render(request, "jobs/list.html", {"jobs": jobs})

