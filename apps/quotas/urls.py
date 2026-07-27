from django.urls import path
from apps.quotas import views as quota_views

app_name = "quotas"

urlpatterns = [
    path('', quota_views.list_quotas, name='list'),
]
