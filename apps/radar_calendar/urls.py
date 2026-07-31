from django.urls import path
from apps.radar_calendar import views

urlpatterns = [
    path("calendar", views.CalendarView.as_view()),
    path("holidays", views.HolidayListCreateView.as_view()),
]
