from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Amenity(models.Model):
    """Model for property amenities."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For frontend icon display
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Amenities'


class Location(models.Model):
    """Model for property locations."""
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default='Lagos')
    state = models.CharField(max_length=100, default='Lagos')
    country = models.CharField(max_length=100, default='Nigeria')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    def __str__(self):
        return self.name


class Property(models.Model):
    """Model for property listings."""
    
    # Property types
    APARTMENT = 'apartment'
    HOUSE = 'house'
    LAND = 'land'
    COMMERCIAL = 'commercial'
    OFFICE = 'office'
    
    PROPERTY_TYPE_CHOICES = [
        (APARTMENT, 'Apartment'),
        (HOUSE, 'House'),
        (LAND, 'Land'),
        (COMMERCIAL, 'Commercial'),
        (OFFICE, 'Office'),
    ]
    
    # Listing types
    FOR_SALE = 'for_sale'
    FOR_RENT = 'for_rent'
    
    LISTING_TYPE_CHOICES = [
        (FOR_SALE, 'For Sale'),
        (FOR_RENT, 'For Rent'),
    ]
    
    # Verification status
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'
    
    VERIFICATION_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (VERIFIED, 'Verified'),
        (REJECTED, 'Rejected'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    address = models.TextField()
    bedrooms = models.PositiveIntegerField(blank=True, null=True)
    bathrooms = models.PositiveIntegerField(blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text='Size in square meters', blank=True, null=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS_CHOICES, default=PENDING)
    rejection_reason = models.TextField(blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_properties')
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']


class PropertyImage(models.Model):
    """Model for property images."""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyDocument(models.Model):
    """Model for property documents."""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='property_documents/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title