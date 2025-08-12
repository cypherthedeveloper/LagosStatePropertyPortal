from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Property, PropertyImage, PropertyDocument, Amenity, Location
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer, PropertyVerificationSerializer,
    PropertyImageSerializer, PropertyDocumentSerializer, AmenitySerializer, LocationSerializer
)
from permissions import (
    IsAdmin, IsGovernmentAgency, IsPropertyOwnerOrRealEstateFirm, 
    IsVerifiedUser, IsOwnerOrAdmin, IsPropertyOwnerOrReadOnly
)


class AmenityViewSet(viewsets.ModelViewSet):
    """ViewSet for Amenity model."""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAdmin]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet for Location model."""
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'city', 'state']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class PropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for Property model."""
    queryset = Property.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'listing_type', 'verification_status', 'bedrooms', 'bathrooms', 'location']
    search_fields = ['title', 'description', 'address', 'location__name']
    ordering_fields = ['price', 'created_at', 'size']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        elif self.action == 'verify':
            return PropertyVerificationSerializer
        return PropertyDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsPropertyOwnerOrRealEstateFirm & IsVerifiedUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action == 'verify':
            permission_classes = [IsAdmin | IsGovernmentAgency]
        elif self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            permission_classes = [IsVerifiedUser]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def verify(self, request, pk=None):
        property_instance = self.get_object()
        serializer = self.get_serializer(property_instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_properties(self, request):
        properties = Property.objects.filter(owner=request.user)
        serializer = PropertyListSerializer(properties, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_verification(self, request):
        if not (request.user.is_admin or request.user.is_government):
            return Response({"detail": "You do not have permission to perform this action."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        properties = Property.objects.filter(verification_status=Property.PENDING)
        serializer = PropertyListSerializer(properties, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        # Get query parameters
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        property_type = request.query_params.get('property_type')
        listing_type = request.query_params.get('listing_type')
        location = request.query_params.get('location')
        min_bedrooms = request.query_params.get('min_bedrooms')
        min_bathrooms = request.query_params.get('min_bathrooms')
        amenities = request.query_params.getlist('amenities')
        
        # Start with all active properties
        queryset = Property.objects.filter(is_active=True, verification_status=Property.VERIFIED)
        
        # Apply filters
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if listing_type:
            queryset = queryset.filter(listing_type=listing_type)
        if location:
            queryset = queryset.filter(Q(location__name__icontains=location) | 
                                      Q(location__city__icontains=location) | 
                                      Q(address__icontains=location))
        if min_bedrooms:
            queryset = queryset.filter(bedrooms__gte=min_bedrooms)
        if min_bathrooms:
            queryset = queryset.filter(bathrooms__gte=min_bathrooms)
        if amenities:
            for amenity in amenities:
                queryset = queryset.filter(amenities__id=amenity)
        
        serializer = PropertyListSerializer(queryset, many=True)
        return Response(serializer.data)


class PropertyImageViewSet(viewsets.ModelViewSet):
    """ViewSet for PropertyImage model."""
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_pk')
        if property_id:
            return PropertyImage.objects.filter(property_id=property_id)
        return PropertyImage.objects.all()
    
    def perform_create(self, serializer):
        property_id = self.kwargs.get('property_pk')
        if property_id:
            property_instance = Property.objects.get(id=property_id)
            if property_instance.owner != self.request.user and not self.request.user.is_admin:
                return Response({"detail": "You do not have permission to add images to this property."}, 
                                status=status.HTTP_403_FORBIDDEN)
            serializer.save(property_id=property_id)
        else:
            serializer.save()


class PropertyDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for PropertyDocument model."""
    queryset = PropertyDocument.objects.all()
    serializer_class = PropertyDocumentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrAdmin]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [IsOwnerOrAdmin | IsGovernmentAgency]
        else:
            permission_classes = [IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_pk')
        if property_id:
            return PropertyDocument.objects.filter(property_id=property_id)
        return PropertyDocument.objects.all()
    
    def perform_create(self, serializer):
        property_id = self.kwargs.get('property_pk')
        if property_id:
            property_instance = Property.objects.get(id=property_id)
            if property_instance.owner != self.request.user and not self.request.user.is_admin:
                return Response({"detail": "You do not have permission to add documents to this property."}, 
                                status=status.HTTP_403_FORBIDDEN)
            serializer.save(property_id=property_id)
        else:
            serializer.save()