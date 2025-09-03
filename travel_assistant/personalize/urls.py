from django.urls import path
from .views import interests, create_preference, update_preference, add_tourist_spot, create_itinerary, get_recommendations

urlpatterns = [
    path('interests/', interests, name='interests-list'),
    path('preferences/create/', create_preference, name='create-preference'),
    path('preferences/update/', update_preference, name='update-preference'),
    path('itineraries/create/', create_itinerary, name='create-itinerary'),
    path('days/<int:day_id>/add-spot/', add_tourist_spot, name='add-tourist-spot'),
    path('recommendations/', get_recommendations, name='get-recommendations'),
]