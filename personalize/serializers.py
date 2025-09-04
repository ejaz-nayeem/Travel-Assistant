from rest_framework import serializers
from .models import Interest, Itinerary, TouristSpot, Day
from django.utils import timezone
from datetime import date

class InterestSerializer(serializers.ModelSerializer):
    """Serializer for listing available interests."""
    class Meta:
        model = Interest
        fields = ['id', 'name']

class UserPreferenceSerializer(serializers.Serializer):
    """Serializer for creating/updating a user's preference list."""
    preferences = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Interest.objects.all()
    )

    def validate_preferences(self, value):
        if not value:
            raise serializers.ValidationError("You must select at least one interest.")
        return value

class ItineraryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new itinerary."""
    class Meta:
        model = Itinerary
        fields = [
            'id', 'destination', 'trip_type', 'budget',
            'duration', 'start_date', 'end_date'
        ]

    def validate(self, data):
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after the start date.")
        return data
    
class TouristSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristSpot
        fields = ['id', 'day', 'name', 'location']
        
class TouristSpotReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TouristSpot
        fields = ['id', 'name', 'location']


class DayReadSerializer(serializers.ModelSerializer):
    spots = TouristSpotReadSerializer(many=True, read_only=True)

    class Meta:
        model = Day
        fields = ['id', 'day_number', 'spots']


class ItineraryReadSerializer(serializers.ModelSerializer):
    days = DayReadSerializer(many=True, read_only=True)
    days_left = serializers.SerializerMethodField()
    planning_progress = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = [
            'id', 'destination', 'trip_type', 'budget',
            'duration', 'start_date', 'end_date', 'days', 
            'days_left', 'planning_progress'
        ]

    def get_days_left(self, obj):
        """
        Calculates the number of days until the trip starts.
        Returns None if the trip has already started or passed.
        """
        today = date.today()
        if obj.start_date > today:
            delta = obj.start_date - today
            return delta.days
        return None # Return None or 0 if the trip is in progress or over
    
    def get_planning_progress(self, obj):
        """
        Calculates the planning progress of the itinerary.
        This is a simplified example. You can make this logic as complex as you need.
        """
        # Example logic: Assume 100% complete if it has at least one activity per day.
        total_days = (obj.end_date - obj.start_date).days + 1
        days_with_activities = obj.days.filter(activities__isnull=False).distinct().count()

        if total_days > 0:
            progress = (days_with_activities / total_days) * 100
            return int(progress)
        return 0
    
class RecommendationRequestSerializer(serializers.Serializer):
    """
    Validates the data for a "What's Happening" recommendation request.
    This is not a ModelSerializer as it represents a query, not a database object.
    """
    # --- User's Current Location (sent from the frontend) ---
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=6, required=True)

    # --- User's Filters ---
    preferences = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Interest.objects.all(),
        required=False # Allow requests with no specific preference
    )
    timing = serializers.ChoiceField(
        choices=['ALL_DAY', 'MORNING', 'AFTERNOON', 'EVENING'],
        default='ALL_DAY'
    )
    distance = serializers.ChoiceField(
        choices=[2, 5, 10], # Kilometers
        default=5
    )