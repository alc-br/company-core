from django.urls import path
from apps.feature_flags import views as ff_views

app_name = "feature_flags"

urlpatterns = [
    path('', ff_views.list_flags, name='list'),
    path('create/', ff_views.create_flag, name='create'),
    path('<int:pk>/edit/', ff_views.edit_flag, name='edit'),
    path('<int:pk>/toggle/', ff_views.toggle_flag, name='toggle'),
    path('<int:pk>/delete/', ff_views.delete_flag, name='delete'),
]
