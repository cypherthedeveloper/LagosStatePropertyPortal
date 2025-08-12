from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Lead(models.Model):
    """Model for property inquiries/leads."""
    
    # Status choices
    NEW = 'new'
    CONTACTED = 'contacted'
    QUALIFIED = 'qualified'
    LOST = 'lost'
    CONVERTED = 'converted'
    
    STATUS_CHOICES = [
        (NEW, 'New'),
        (CONTACTED, 'Contacted'),
        (QUALIFIED, 'Qualified'),
        (LOST, 'Lost'),
        (CONVERTED, 'Converted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leads')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='leads')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.property.title}"
    
    class Meta:
        ordering = ['-created_at']


class Message(models.Model):
    """Model for messages between users regarding a property."""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email}"
    
    class Meta:
        ordering = ['created_at']