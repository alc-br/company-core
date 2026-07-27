from django.urls import path
from apps.billing import views as billing_views

app_name = "billing"

urlpatterns = [
    path('', billing_views.list_plans, name='plans'),
    path('subscriptions/', billing_views.list_subscriptions, name='subscriptions'),
]
