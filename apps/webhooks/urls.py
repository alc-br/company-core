from django.urls import path
from apps.webhooks import views as wh_views

app_name = "webhooks"

urlpatterns = [
    path('', wh_views.list_endpoints, name='endpoints'),
    path('deliveries/', wh_views.list_deliveries, name='deliveries'),
]
