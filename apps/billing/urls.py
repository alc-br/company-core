from django.urls import path
from apps.billing import views as billing_views

app_name = "billing"

urlpatterns = [
    path('', billing_views.list_plans, name='plans'),
    path('subscriptions/', billing_views.list_subscriptions, name='subscriptions'),
    path('plans/create/', billing_views.create_plan, name='create_plan'),
    path('plans/<int:pk>/edit/', billing_views.edit_plan, name='edit_plan'),
    path('plans/<int:pk>/delete/', billing_views.delete_plan, name='delete_plan'),
    path('webhook/stripe/', billing_views.stripe_webhook_view, name='stripe_webhook'),
]
