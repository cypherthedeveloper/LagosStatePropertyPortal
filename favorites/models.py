from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Favorite(models.Model):
    """Model for user's favorite properties."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'property')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.property.title}"