from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import KYCVerification

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirmation = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'password_confirmation', 
                  'role', 'phone_number', 'address', 'profile_picture', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'is_verified', 'date_joined']
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirmation'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.BUYER_RENTER),
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            profile_picture=validated_data.get('profile_picture', None),
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'profile_picture']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change endpoint."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class KYCVerificationSerializer(serializers.ModelSerializer):
    """Serializer for KYC verification."""
    
    class Meta:
        model = KYCVerification
        fields = ['id', 'user', 'status', 'submitted_at', 'verified_at', 'verified_by', 'rejection_reason']
        read_only_fields = ['id', 'user', 'submitted_at', 'verified_at', 'verified_by', 'rejection_reason']


class KYCSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for submitting KYC verification documents."""
    
    class Meta:
        model = User
        fields = ['id_type', 'id_number', 'id_document', 'business_name', 
                  'business_registration_number', 'business_document']
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        # Validate based on user role
        if user.role in [User.PROPERTY_OWNER, User.BUYER_RENTER]:
            if not attrs.get('id_type') or not attrs.get('id_number') or not attrs.get('id_document'):
                raise serializers.ValidationError("ID type, number, and document are required for individual verification.")
        
        if user.role == User.REAL_ESTATE_FIRM:
            if not attrs.get('business_name') or not attrs.get('business_registration_number') or not attrs.get('business_document'):
                raise serializers.ValidationError("Business name, registration number, and document are required for business verification.")
        
        return attrs


class KYCVerificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating KYC verification status."""
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = KYCVerification
        fields = ['status', 'rejection_reason']
    
    def validate(self, attrs):
        if attrs.get('status') == KYCVerification.REJECTED and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is required when rejecting a verification."})
        return attrs
    
    def update(self, instance, validated_data):
        user = instance.user
        status = validated_data.get('status')
        
        instance.status = status
        if status == KYCVerification.REJECTED:
            instance.rejection_reason = validated_data.get('rejection_reason')
            user.is_verified = False
        elif status == KYCVerification.APPROVED:
            user.is_verified = True
            instance.verified_by = self.context['request'].user
            instance.verified_at = serializers.DateTimeField().to_representation(serializers.DateTimeField().to_internal_value(serializers.DateTimeField().to_representation(serializers.DateTimeField().get_default())))
        
        user.save()
        instance.save()
        return instance