from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import SupportTicketSerializer
from django.core.mail import send_mail
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_support_ticket(request):
    """
    Creates a new support ticket from an authenticated user.
    The user's email is automatically used.
    """
    serializer = SupportTicketSerializer(data=request.data)
    if serializer.is_valid():
        # Save the ticket to the database, linking it to the current user
        ticket = serializer.save(user=request.user)

        # The user's email is now taken directly from their profile
        user_email = request.user.email

        # Send an email notification to the support team
        try:
            subject = f"New Support Ticket #{ticket.id} from {user_email}"
            message = f"""
            A new support ticket has been submitted.

            User: {request.user.username} (ID: {request.user.id})
            Reply-to Email: {user_email}
            Submitted At: {ticket.created_at.strftime('%Y-%m-%d %H:%M:%S')}

            Description:
            {ticket.description}
            """
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                # Using the official support email address
                recipient_list=['travel_assistant@support.com'],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending support ticket email: {e}")

        return Response({"message": "Your support request has been submitted successfully."}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
