import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from dateutil.relativedelta import relativedelta
from .models import Subscription
from accounts.models import CustomUser
from rest_framework.decorators import api_view, permission_classes

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_status(request):
    """
    An endpoint to check the user's current subscription status.
    Requires authentication.
    """
    user = request.user
    
    # Check for an active paid subscription first
    if hasattr(user, 'subscription') and user.subscription.is_active():
        return Response({
            "plan": user.subscription.get_plan_type_display(),
            "status": "Active",
            "subscription_ends": user.subscription.end_date
        })
    
    # If no paid plan, check for an active free trial
    if user.trial_end_date and user.trial_end_date > timezone.now():
        return Response({
            "plan": "Free Trial",
            "status": "Active",
            "trial_ends": user.trial_end_date
        })
    
    # Otherwise, no active plan
    return Response({"plan": "None", "status": "Inactive"})

# --- Function 2: Upgrade Subscription Plan ---
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upgrade_plan(request):
    """
    Endpoint to initiate a Stripe Checkout session to upgrade a plan.
    Requires authentication.
    """
    user = request.user

    # Check if user already has an active subscription
    if hasattr(user, 'subscription') and user.subscription.is_active():
        return Response({"message": "You already have an active subscription."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the incoming price_id
    price_id = request.data.get('price_id')
    if not price_id:
        return Response({"error": "A price_id is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_prices = [settings.STRIPE_BASIC_PRICE_ID, settings.STRIPE_PREMIUM_PRICE_ID]
    if price_id not in valid_prices:
        return Response({"error": "Invalid price_id."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the Stripe Checkout Session
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            metadata={'user_id': user.id, 'price_id': price_id},
            success_url='http://localhost:3000/success', # CHANGE TO YOUR FRONTEND SUCCESS URL
            cancel_url='http://localhost:3000/cancel',   # CHANGE TO YOUR FRONTEND CANCEL URL
        )
        return Response({'checkout_url': checkout_session.url})
    except Exception as e:
        return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# payment/views.py

@csrf_exempt
def stripe_webhook(request):
    print("--- Webhook Request Received ---")
    print(f"Headers: {request.headers}")
    # --- END DIAGNOSIS ---

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE') # or request.headers.get('Stripe-Signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return HttpResponse(status=400, content=str(e))

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session.mode == 'subscription' and session.metadata.get('user_id'):
            user_id = int(session.metadata.get('user_id'))
            
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                print(f"Webhook Error: User with ID {user_id} not found.")
                return HttpResponse(status=400, content=f"User not found: {user_id}")

            price_id = session.metadata.get('price_id')
            stripe_sub_id = session.get('subscription')

            # --- IMPROVED PRICE ID VALIDATION ---
            if price_id == settings.STRIPE_BASIC_PRICE_ID:
                plan_type = Subscription.Plan.BASIC
            elif price_id == settings.STRIPE_PREMIUM_PRICE_ID:
                plan_type = Subscription.Plan.PREMIUM
            else:
                # This is the likely cause of your error.
                print(f"Webhook Error: Unrecognized price_id '{price_id}' for user {user_id}.")
                return HttpResponse(status=400, content=f"Unrecognized price_id: {price_id}")
            # --- END OF IMPROVEMENT ---
            
            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan_type': plan_type,
                    'stripe_subscription_id': stripe_sub_id,
                    'status': Subscription.Status.ACTIVE,
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + relativedelta(months=1),
                }
            )
            user.trial_end_date = None
            user.save()
            print(f"Webhook Success: Subscription created for user {user.username}.")
    else:
        print(f"Received unhandled event type: {event['type']}")

    return HttpResponse(status=200)