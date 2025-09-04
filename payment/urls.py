from django.urls import path
from .views import subscription_status, upgrade_plan, stripe_webhook

urlpatterns = [
    path('status/', subscription_status, name='subscription-status'),
    path('upgrade-plan/', upgrade_plan, name='upgrade-plan'),
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]