from django.urls import path
from .views import (event_list_create, event_detail, my_event_list, user_invite_list, send_invite,
                    notification_list,
                    mark_all_notifications_as_read,
                    mark_notification_as_read,
                    respond_to_invitation,
                    toggle_bookmark,        
                    bookmarked_events_list
                    )

urlpatterns = [
    # For "Event For You" and "Create Event"
    path('events/', event_list_create, name='event-list-create'),

    # For "My Event" tab
    path('events/my-events/', my_event_list, name='my-event-list'),

    # For viewing, updating, and deleting a specific event
    path('events/<int:pk>/', event_detail, name='event-detail'),
    path('events/<int:event_id>/invite-list/', user_invite_list, name='user-invite-list'),
    
    # To send an invitation to a specific user for a specific event
    path('events/<int:event_id>/invite/<int:user_id>/', send_invite, name='send-invite'),
    # Get the list of all notifications for the logged-in user
    path('notifications/', notification_list, name='notification-list'),

    # Mark all notifications as read
    path('notifications/mark-all-as-read/', mark_all_notifications_as_read, name='notifications-mark-all-read'),
    # Mark a single notification as read (e.g., /api/events/notifications/5/mark-as-read/)
    path('notifications/<int:invitation_id>/mark-as-read/', mark_notification_as_read, name='notification-mark-read'),

    # Respond to a specific invitation (e.g., /api/events/invitations/5/respond/)
    path('invitations/<int:invitation_id>/respond/', respond_to_invitation, name='respond-to-invitation'),
    # To add or remove a bookmark for a specific event
    path('events/<int:event_id>/bookmark/', toggle_bookmark, name='event-bookmark-toggle'),

    # To get the list of all of the user's bookmarked events
    path('bookmarks/', bookmarked_events_list, name='bookmark-list'),
]

