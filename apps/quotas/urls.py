from django.urls import path
from apps.quotas import views as quota_views

app_name = "quotas"

urlpatterns = [
    path('', quota_views.list_quotas, name='list'),
    path('create/', quota_views.create_quota, name='create'),
    path('<int:pk>/edit/', quota_views.edit_quota, name='edit'),
    path('<int:pk>/delete/', quota_views.delete_quota, name='delete'),
]
