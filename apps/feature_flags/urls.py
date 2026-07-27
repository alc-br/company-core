from django.urls import path
from apps.feature_flags import views as ff_views

app_name = "feature_flags"

urlpatterns = [
    path('', ff_views.list_flags, name='list'),
]
