from django.urls import path
from apps.settings import views as settings_views

app_name = "settings"

urlpatterns = [
    path('', settings_views.view_settings, name='view'),
    path('<int:pk>/edit/', settings_views.edit_setting, name='edit'),
]
