from rest_framework import serializers
from .models import Event, Invitation
from personalize.serializers import InterestSerializer # Reuse for tag details
from accounts.models import CustomUser

class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating events."""
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'image', 'category', 'event_date',
            'start_time', 'end_time', 'venue_name', 'address', 'tags',
            'organizer_name', 'organizer_email', 'organizer_phone', 'organizer_website'
        ]

class EventListSerializer(serializers.ModelSerializer):
    """A lightweight serializer for the event list view."""
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'image', 'event_date', 'start_time',
            'venue_name', 'address'
        ]

class EventDetailSerializer(serializers.ModelSerializer):
    """A detailed serializer for the single event view."""
    tags = InterestSerializer(many=True, read_only=True) # Show full tag details
    class Meta:
        model = Event
        exclude = ['organizer'] # Exclude the user ID, but show everything else
        
class UserInviteListSerializer(serializers.ModelSerializer):
    """A lightweight serializer to list users for inviting."""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name'] # Add profile pic field if you have one

class InvitationSerializer(serializers.ModelSerializer):
    """Serializer for creating and viewing invitations."""
    class Meta:
        model = Invitation
        fields = ['id', 'event', 'inviter', 'invitee', 'status']
        read_only_fields = ['inviter', 'status']
        
class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer to display invitation notifications.
    Includes nested data about the inviter and the event.
    """
    # Use a lightweight serializer for the inviter to avoid sending sensitive user data
    inviter = serializers.StringRelatedField(read_only=True)
    
    # Use a lightweight serializer for the event
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_id = serializers.IntegerField(source='event.id', read_only=True)

    class Meta:
        model = Invitation
        fields = [
            'id', 
            'inviter', 
            'event_id',
            'event_title',
            'status',
            'is_read',
            'created_at'
        ]