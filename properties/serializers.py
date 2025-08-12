from rest_framework import serializers
from django.utils import timezone
from .models import Property, PropertyImage, PropertyDocument, Amenity, Location


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for the Amenity model."""
    
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for the Location model."""
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'state', 'country', 'latitude', 'longitude']


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for the PropertyImage model."""
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image', 'is_primary', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class PropertyDocumentSerializer(serializers.ModelSerializer):
    """Serializer for the PropertyDocument model."""
    
    class Meta:
        model = PropertyDocument
        fields = ['id', 'property', 'document', 'title', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for listing properties with minimal information."""
    location = LocationSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    amenities = AmenitySerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'price', 'property_type', 'listing_type', 'location', 
                  'bedrooms', 'bathrooms', 'size', 'primary_image', 'amenities', 
                  'verification_status', 'owner_name', 'created_at']
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()
        if primary_image:
            return primary_image.image.url
        return None
    
    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}"


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed property information."""
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), write_only=True, source='location')
    images = PropertyImageSerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    amenity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(), write_only=True, source='amenities', many=True, required=False)
    owner_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'description', 'price', 'property_type', 'listing_type', 
                  'location', 'location_id', 'address', 'bedrooms', 'bathrooms', 'size', 
                  'amenities', 'amenity_ids', 'owner', 'owner_name', 'verification_status', 
                  'rejection_reason', 'verified_by', 'verified_at', 'created_at', 'updated_at', 
                  'is_featured', 'is_active', 'images', 'documents']
        read_only_fields = ['id', 'owner', 'verification_status', 'rejection_reason', 
                           'verified_by', 'verified_at', 'created_at', 'updated_at']
    
    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}"
    
    def create(self, validated_data):
        amenities = validated_data.pop('amenities', [])
        property_instance = Property.objects.create(**validated_data, owner=self.context['request'].user)
        property_instance.amenities.set(amenities)
        return property_instance
    
    def update(self, instance, validated_data):
        amenities = validated_data.pop('amenities', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if amenities is not None:
            instance.amenities.set(amenities)
        
        return instance


class PropertyVerificationSerializer(serializers.ModelSerializer):
    """Serializer for property verification."""
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Property
        fields = ['verification_status', 'rejection_reason']
    
    def validate(self, attrs):
        if attrs.get('verification_status') == Property.REJECTED and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is required when rejecting a property."})
        return attrs
    
    def update(self, instance, validated_data):
        instance.verification_status = validated_data.get('verification_status')
        if instance.verification_status == Property.REJECTED:
            instance.rejection_reason = validated_data.get('rejection_reason')
        elif instance.verification_status == Property.VERIFIED:
            instance.verified_by = self.context['request'].user
            instance.verified_at = timezone.now()
            instance.rejection_reason = None
        
        instance.save()
        return instance