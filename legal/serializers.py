from rest_framework import serializers
from .models import LegalPage

class LegalPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalPage
        fields = ['title', 'content', 'last_updated']