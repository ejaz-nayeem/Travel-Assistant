from django.db import models
from django.conf import settings
from django.utils import timezone

class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        
    class Plan(models.TextChoices):
        BASIC = 'BASIC', 'Basic'
        PREMIUM = 'PREMIUM', 'Premium'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan_type = models.CharField(max_length=10, choices=Plan.choices)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def is_active(self):
        """Checks if the subscription is currently active."""
        return self.end_date > timezone.now() and self.status == self.Status.ACTIVE

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_type_display()} ({self.get_status_display()})"
