from django.urls import path
from apps.notifications import views as notif_views

app_name = "notifications"

urlpatterns = [
    path('', notif_views.list_notifications, name='list'),
]
