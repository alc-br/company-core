from django.urls import path
from apps.permissions import views as perm_views

app_name = "permissions"

urlpatterns = [
    path('', perm_views.list_permissions, name='list'),
    path('roles/', perm_views.list_roles, name='roles'),
]
