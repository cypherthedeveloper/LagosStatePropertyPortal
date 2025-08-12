from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Favorite
from .serializers import FavoriteSerializer
from permissions import IsOwnerOrAdmin


class FavoriteViewSet(viewsets.ModelViewSet):
    """ViewSet for Favorite model."""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        # Check if the favorite already exists
        property_id = request.data.get('property')
        existing_favorite = Favorite.objects.filter(user=request.user, property_id=property_id).first()
        
        if existing_favorite:
            return Response({"detail": "This property is already in your favorites."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)