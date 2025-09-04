from django.contrib import admin
from .models import SupportTicket

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    # --- Corrected list_display ---
    # We display the 'user_email' custom method instead of the old 'email' field.
    list_display = ('id', 'user', 'user_email', 'status', 'created_at')
    
    list_filter = ('status', 'created_at')
    search_fields = ('description', 'user__username', 'user__email')
    
    # --- Corrected readonly_fields ---
    # The 'email' field is gone. We can also add user_email here.
    readonly_fields = ('user', 'user_email', 'description', 'created_at')

    # This is a special method to allow displaying fields from a related model.
    @admin.display(description='User Email')
    def user_email(self, obj):
        return obj.user.email