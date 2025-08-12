from rest_framework import serializers
from .models import Favorite
from properties.serializers import PropertyListSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for the Favorite model."""
    property_details = PropertyListSerializer(source='property', read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'property', 'property_details', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']