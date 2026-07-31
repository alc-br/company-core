from django.urls import path
from apps.radar_portal import views

urlpatterns = [
    path("portal/login", views.portal_login),
    path("portal/logout", views.portal_logout),
    path("portal/me", views.PortalMeView.as_view()),
    path("announcements", views.AnnouncementListView.as_view()),
]
