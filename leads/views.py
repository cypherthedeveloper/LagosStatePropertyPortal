from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Lead, Message
from .serializers import LeadSerializer, MessageSerializer
from permissions import IsOwnerOrAdmin


class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet for Lead model."""
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'property']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        # Property owners see leads for their properties
        if user.is_property_owner or user.is_real_estate_firm:
            return Lead.objects.filter(property__owner=user)
        # Buyers/renters see their own leads
        return Lead.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        lead = self.get_object()
        status_value = request.data.get('status')
        
        if not status_value or status_value not in dict(Lead.STATUS_CHOICES).keys():
            return Response({"detail": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Only property owner can update lead status
        if request.user != lead.property.owner and not request.user.is_admin:
            return Response({"detail": "You do not have permission to update this lead's status."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        lead.status = status_value
        lead.save()
        
        serializer = self.get_serializer(lead)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model."""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(lead__id=self.kwargs.get('lead_pk'))
    
    def create(self, request, *args, **kwargs):
        lead_id = self.kwargs.get('lead_pk')
        lead = Lead.objects.get(id=lead_id)
        
        # Check if user is either the lead creator or the property owner
        if request.user != lead.user and request.user != lead.property.owner and not request.user.is_admin:
            return Response({"detail": "You do not have permission to send messages for this lead."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(lead_id=lead_id)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def unread(self, request, lead_pk=None):
        messages = Message.objects.filter(lead__id=lead_pk, receiver=request.user, is_read=False)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None, lead_pk=None):
        message = self.get_object()
        
        # Only the receiver can mark a message as read
        if request.user != message.receiver:
            return Response({"detail": "You do not have permission to mark this message as read."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        message.is_read = True
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)