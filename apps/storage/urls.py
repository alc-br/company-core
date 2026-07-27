from django.urls import path
from apps.storage import views as storage_views

app_name = "storage"

urlpatterns = [
    path('', storage_views.list_files, name='list'),
]
