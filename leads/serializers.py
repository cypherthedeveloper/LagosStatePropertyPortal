from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Lead, Message
from properties.serializers import PropertyListSerializer

User = get_user_model()


class LeadSerializer(serializers.ModelSerializer):
    """Serializer for the Lead model."""
    property_details = PropertyListSerializer(source='property', read_only=True)
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = ['id', 'user', 'property', 'property_details', 'user_details', 'status', 'message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'name': f"{obj.user.first_name} {obj.user.last_name}",
            'phone_number': obj.user.phone_number
        }


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for the Message model."""
    sender_details = serializers.SerializerMethodField()
    receiver_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'lead', 'sender', 'receiver', 'sender_details', 'receiver_details', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'is_read', 'created_at']
    
    def get_sender_details(self, obj):
        return {
            'id': obj.sender.id,
            'email': obj.sender.email,
            'name': f"{obj.sender.first_name} {obj.sender.last_name}"
        }
    
    def get_receiver_details(self, obj):
        return {
            'id': obj.receiver.id,
            'email': obj.receiver.email,
            'name': f"{obj.receiver.first_name} {obj.receiver.last_name}"
        }
    
    def create(self, validated_data):
        sender = self.context['request'].user
        lead = validated_data.get('lead')
        
        # Determine the receiver based on the lead
        if sender == lead.user:
            # If sender is the lead creator, receiver is the property owner
            receiver = lead.property.owner
        else:
            # If sender is the property owner, receiver is the lead creator
            receiver = lead.user
        
        message = Message.objects.create(
            lead=lead,
            sender=sender,
            receiver=receiver,
            content=validated_data.get('content')
        )
        
        return message