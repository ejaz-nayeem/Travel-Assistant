from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Event, Invitation
from accounts.models import CustomUser
from django.shortcuts import get_object_or_404
from .serializers import EventListSerializer, EventDetailSerializer, EventCreateSerializer, InvitationSerializer, UserInviteListSerializer, NotificationSerializer

# --- View for Listing All Events and Creating a New Event ---
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def event_list_create(request):
    """
    - GET: List all events (publicly accessible).
    - POST: Create a new event (requires authentication).
    """
    # --- Logic for GET (Listing all events) ---
    if request.method == 'GET':
        events = Event.objects.all().order_by('-event_date')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    # --- Logic for POST (Creating a new event) ---
    elif request.method == 'POST':
        # The @permission_classes decorator already ensures the user is authenticated.
        serializer = EventCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Assign the logged-in user as the organizer before saving.
            serializer.save(organizer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- View for "My Events" Tab ---
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_event_list(request):
    """
    List only the events created by the currently authenticated user.
    """
    # The decorator ensures request.user exists.
    events = Event.objects.filter(organizer=request.user).order_by('-event_date')
    serializer = EventListSerializer(events, many=True)
    return Response(serializer.data)

# --- View for Detail, Update, and Delete actions ---
@api_view(['GET', 'PUT', 'DELETE'])
# We handle permissions manually inside the function for this view.
def event_detail(request, pk):
    """
    - GET: Retrieve a single event (publicly accessible).
    - PUT: Update an event (organizer only).
    - DELETE: Delete an event (organizer only).
    """
    try:
        event = Event.objects.get(pk=pk)
    except Event.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

    # --- Logic for GET (Viewing a single event) ---
    if request.method == 'GET':
        serializer = EventDetailSerializer(event)
        return Response(serializer.data)

    # --- The following methods require the user to be the organizer ---
    # Manual Permission Check: Is the request user the organizer of the event?
    if event.organizer != request.user:
        return Response(
            {"error": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )

    # --- Logic for PUT (Updating an event) ---
    elif request.method == 'PUT':
        # We use EventCreateSerializer as it's designed for writing data.
        serializer = EventCreateSerializer(event, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # --- Logic for DELETE (Deleting an event) ---
    elif request.method == 'DELETE':
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_invite_list(request, event_id):
    """
    Returns a list of users who can be invited to a specific event.
    Excludes the current user, the event organizer, and anyone already invited.
    """
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get IDs of users who have already been invited to this event
    already_invited_ids = Invitation.objects.filter(event=event).values_list('invitee__id', flat=True)
    
    # Get all users, excluding the current user, the organizer, and those already invited
    users_to_invite = CustomUser.objects.exclude(
        id__in=[request.user.id, event.organizer.id, *already_invited_ids]
    )

    serializer = UserInviteListSerializer(users_to_invite, many=True)
    return Response(serializer.data)

# --- NEW VIEW TO SEND AN INVITATION ---
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_invite(request, event_id, user_id):
    """
    Creates an invitation from the request user to another user for a specific event.
    """
    try:
        event = Event.objects.get(pk=event_id)
        invitee = CustomUser.objects.get(pk=user_id)
    except (Event.DoesNotExist, CustomUser.DoesNotExist):
        return Response({"error": "Event or User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validation checks
    if invitee == request.user:
        return Response({"error": "You cannot invite yourself."}, status=status.HTTP_400_BAD_REQUEST)
    if Invitation.objects.filter(event=event, invitee=invitee).exists():
        return Response({"error": "This user has already been invited."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the invitation
    invitation = Invitation.objects.create(
        event=event,
        inviter=request.user,
        invitee=invitee
    )
    
    # You could add logic here to send a push notification or email to the invitee
    
    serializer = InvitationSerializer(invitation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_list(request):
    """
    Lists all event invitations received by the currently logged-in user.
    """
    invitations = Invitation.objects.filter(invitee=request.user)
    serializer = NotificationSerializer(invitations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_as_read(request):
    """
    Marks all of the user's received invitations as read.
    """
    Invitation.objects.filter(invitee=request.user, is_read=False).update(is_read=True)
    return Response({"message": "All notifications marked as read."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_invitation(request, invitation_id):
    """
    Allows a user to accept or decline a specific invitation.
    Expects a body like: {"response": "accept"} or {"response": "decline"}
    """
    invitation = get_object_or_404(Invitation, pk=invitation_id, invitee=request.user)
    
    response = request.data.get('response', '').lower()

    if invitation.status != 'PENDING':
        return Response({"error": "This invitation has already been responded to."}, status=status.HTTP_400_BAD_REQUEST)

    if response == 'accept':
        invitation.status = 'ACCEPTED'
        # Also add the user to the event's attendee list
        invitation.event.attendees.add(request.user)
    elif response == 'decline':
        invitation.status = 'DECLINED'
    else:
        return Response({"error": "Invalid response. Please provide 'accept' or 'decline'."}, status=status.HTTP_400_BAD_REQUEST)

    # Mark as read since the user is interacting with it.
    invitation.is_read = True
    invitation.save()
    
    serializer = NotificationSerializer(invitation)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_as_read(request, invitation_id):
    """
    Marks a single, specific invitation notification as read.
    """
    # Find the invitation, ensuring it belongs to the logged-in user to prevent
    # one user from marking another's notifications as read.
    invitation = get_object_or_404(Invitation, pk=invitation_id, invitee=request.user)

    # If it's not already read, update it.
    if not invitation.is_read:
        invitation.is_read = True
        invitation.save(update_fields=['is_read'])

    return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_bookmark(request, event_id):
    """
    Toggles a bookmark for an event for the current user.
    If the event is already bookmarked, it will be removed.
    If it's not bookmarked, it will be added.
    """
    user = request.user
    event = get_object_or_404(Event, pk=event_id)

    # Check if the user has already bookmarked this event
    if event in user.bookmarked_events.all():
        # If yes, remove it
        user.bookmarked_events.remove(event)
        return Response({"message": "Bookmark removed successfully."}, status=status.HTTP_200_OK)
    else:
        # If no, add it
        user.bookmarked_events.add(event)
        return Response({"message": "Event bookmarked successfully."}, status=status.HTTP_201_CREATED)

# --- NEW VIEW TO LIST ALL BOOKMARKED EVENTS ---
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def bookmarked_events_list(request):
    """
    Returns a list of all events bookmarked by the currently authenticated user.
    """
    user = request.user
    bookmarked_events = user.bookmarked_events.all().order_by('-created_at')
    
    # We can reuse the EventListSerializer as it contains the right info for a list
    serializer = EventListSerializer(bookmarked_events, many=True)
    return Response(serializer.data)
