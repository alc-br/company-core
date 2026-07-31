from django.urls import path
from apps.radar_reports import views

urlpatterns = [
    path("dashboard", views.DashboardView.as_view()),
    path("reports", views.ReportsView.as_view()),
    path("exports", views.ExportView.as_view()),
]
