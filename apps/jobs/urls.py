from django.urls import path
from apps.jobs import views as job_views

app_name = "jobs"

urlpatterns = [
    path('', job_views.list_jobs, name='list'),
]
