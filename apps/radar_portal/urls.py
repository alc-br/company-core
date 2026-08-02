from django.urls import path
from apps.radar_portal import views, data_views

urlpatterns = [
    path("portal/login", views.portal_login),
    path("portal/logout", views.portal_logout),
    path("portal/me", views.PortalMeView.as_view()),
    path("announcements", views.AnnouncementListView.as_view()),
    path("portal/tasks", data_views.PortalTaskListView.as_view()),
    path("portal/tasks/<int:pk>", data_views.PortalTaskDetailView.as_view()),
    path("portal/tasks/<int:pk>/comments", data_views.PortalTaskCommentView.as_view()),
    path("portal/document-requests", data_views.PortalDocumentRequestListView.as_view()),
    path("portal/documents", data_views.PortalDocumentListView.as_view()),
    path("portal/calendar", data_views.PortalCalendarView.as_view()),
    path("portal/profile", data_views.PortalProfileView.as_view()),
    path("portal/change-password", data_views.PortalChangePasswordView.as_view()),
]
