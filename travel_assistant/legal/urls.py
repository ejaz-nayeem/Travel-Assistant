from django.urls import path
from .views import legal_page_detail

urlpatterns = [
    # The URL will capture the slug, e.g., /api/legal/terms-and-conditions/
    path('<slug:slug>/', legal_page_detail, name='legal-page-detail'),
]