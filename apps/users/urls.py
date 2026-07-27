from django.urls import path
from apps.users.views import profile_view, profile_edit_view

app_name = "users"

urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("profile/edit/", profile_edit_view, name="profile_edit"),
]
