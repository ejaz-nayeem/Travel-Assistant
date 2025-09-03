from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import LegalPage
from .serializers import LegalPageSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def legal_page_detail(request, slug):
    """
    Fetches and returns the content of a legal page (e.g., terms-and-conditions)
    for any authenticated user to view.
    """
    # Find the page by its unique slug, or return a 404 error if it doesn't exist.
    page = get_object_or_404(LegalPage, slug=slug)
    serializer = LegalPageSerializer(page)
    return Response(serializer.data)
