from django.db import models
from django.conf import settings
from personalize.models import Interest # Reusing Interest model for tags

class Event(models.Model):
    # --- CHOICES FOR CATEGORY DROPDOWN ---
    CATEGORY_CHOICES = [
        ('MUSIC', 'Music'),
        ('TECHNOLOGY', 'Technology'),
        ('FOOD_DRINK', 'Food & Drink'),
        ('OUTDOOR', 'Outdoor'),
        ('SPORTS', 'Sports'),
        ('ART_CULTURE', 'Art & Culture'),
        ('EDUCATION', 'Education'),
        ('HEALTH_WELLNESS', 'Health & Wellness'),
    ]

    # --- RELATIONSHIPS ---
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    tags = models.ManyToManyField(Interest, blank=True, related_name='events')
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='attended_events', blank=True)

    # --- BASIC INFORMATION ---
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    # --- DATE & TIME ---
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # --- LOCATION ---
    venue_name = models.CharField(max_length=255)
    address = models.TextField()

    # --- ORGANIZER DETAILS ---
    organizer_name = models.CharField(max_length=100)
    organizer_email = models.EmailField()
    organizer_phone = models.CharField(max_length=20)
    organizer_website = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_invitations')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only be invited to the same event once.
        unique_together = ('event', 'invitee')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.inviter.username} invited {self.invitee.username} to {self.event.title}"
