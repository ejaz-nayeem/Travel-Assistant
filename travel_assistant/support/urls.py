from django.urls import path
from .views import submit_support_ticket

urlpatterns = [
    path('submit/', submit_support_ticket, name='submit-support-ticket'),
]