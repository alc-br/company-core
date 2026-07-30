from django.urls import path
from apps.organizations import views as org_views

app_name = "organizations"

urlpatterns = [
    path('', org_views.list_organizations, name='list'),
    path('create/', org_views.create_organization, name='create'),
    path('<int:org_id>/', org_views.detail_organization, name='detail'),
    path('<int:org_id>/edit/', org_views.edit_organization, name='edit'),
    path('<int:org_id>/delete/', org_views.delete_organization, name='delete'),
    path('switch/', org_views.switch_organization, name='switch'),
    path('invite/', org_views.invite_member, name='invite'),
]
