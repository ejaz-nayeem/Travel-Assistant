from django.db import models
from django.conf import settings

class SupportTicket(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        IN_PROGRESS = 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'

    # The user field is now the single source of truth for who submitted the ticket
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    
    # --- The `email` field is no longer needed here ---
    
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # We get the email from the related user object
        return f"Ticket #{self.id} from {self.user.email} ({self.status})"

    class Meta:
        ordering = ['-created_at']
