from django.contrib import admin
from .models import Interest, Itinerary

admin.site.register(Interest)
admin.site.register(Itinerary) # Also register Itinerary for easy viewing
