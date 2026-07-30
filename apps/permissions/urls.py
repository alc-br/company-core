from django.urls import path
from apps.permissions import views as perm_views

app_name = "permissions"

urlpatterns = [
    path('', perm_views.list_permissions, name='list'),
    path('roles/', perm_views.list_roles, name='roles'),
    path('roles/create/', perm_views.create_role, name='create_role'),
    path('roles/<int:pk>/edit/', perm_views.edit_role, name='edit_role'),
    path('roles/<int:pk>/delete/', perm_views.delete_role, name='delete_role'),
]
