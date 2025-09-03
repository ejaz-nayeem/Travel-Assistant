from django.urls import path
from .views import SubscriptionStatusView, UpgradePlanView, stripe_webhook

urlpatterns = [
    # API endpoints for your frontend to call
    path('status/', SubscriptionStatusView.as_view(), name='subscription-status'),
    path('upgrade-plan/', UpgradePlanView.as_view(), name='upgrade-plan'),

    # Webhook URL for Stripe to call
    path('stripe-webhook/', stripe_webhook, name='stripe-webhook'),
]