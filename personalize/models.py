from django.db import models
from django.conf import settings

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# personalize/models.py

class Itinerary(models.Model):
    # --- CHOICES FOR THE DROPDOWNS ---
    TRIP_TYPES = [('SOLO', 'Solo'), ('COUPLE', 'Couple'), ('FAMILY', 'Family'), ('GROUP', 'Group')]
    BUDGETS = [('50-100', '$50/100 day'), ('100-200', '$100/200 day'), ('200-300', '$200/300 day'), ('300-500+', '$300/500+ day')]
    DURATIONS = [('3_DAYS', '3 days'), ('5_DAYS', '5 days'), ('1_WEEK', '1 week'), ('10_DAYS', '10 days'), ('2_WEEKS', '2 weeks')]

    # --- MODEL FIELDS ---
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='itineraries')
    destination = models.CharField(max_length=255) # <-- You will likely get asked about this too
    
    # --- ADD DEFAULTS TO THESE FIELDS ---
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPES, default='SOLO')
    budget = models.CharField(max_length=10, choices=BUDGETS, default='50-100')
    duration = models.CharField(max_length=10, choices=DURATIONS, default='3_DAYS')
    
    # For dates, a good default is often the current date. Make sure to import it.
    # from django.utils import timezone
    start_date = models.DateField() # <-- Django will ask about this too.
    end_date = models.DateField()   # <-- And this.
    
class Day(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveIntegerField()  # Day 1, Day 2, Day 3, ...

    def __str__(self):
        return f"Day {self.day_number} of {self.itinerary.destination}"


class TouristSpot(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="spots")
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.location}) on {self.day}"