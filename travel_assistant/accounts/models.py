from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    trial_end_date = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(unique=True) 
    preferences = models.ManyToManyField('personalize.Interest', blank=True, related_name="users")
    bookmarked_events = models.ManyToManyField('events.Event', blank=True, related_name="bookmarked_by")
    

    USERNAME_FIELD = 'email'        # login with email instead of username
    REQUIRED_FIELDS = ['username']  # still require username at registration

    def __str__(self):
        return self.email

@receiver(post_save, sender=CustomUser)
def set_free_trial(sender, instance, created, **kwargs):
    if created and not instance.trial_end_date:
        instance.trial_end_date = timezone.now() + timedelta(days=7)
        instance.save()
