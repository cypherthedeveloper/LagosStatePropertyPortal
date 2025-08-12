from rest_framework import viewsets, status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import KYCVerification
from .serializers import (
    UserSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    KYCVerificationSerializer, KYCSubmissionSerializer, KYCVerificationUpdateSerializer
)
from permissions import IsAdmin, IsGovernmentAgency, IsVerifiedUser

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'change_password']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve', 'destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class KYCVerificationViewSet(viewsets.ModelViewSet):
    """ViewSet for KYC verification."""
    queryset = KYCVerification.objects.all()
    serializer_class = KYCVerificationSerializer
    
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            permission_classes = [IsAdmin | IsGovernmentAgency]
        elif self.action == 'list':
            permission_classes = [IsAdmin | IsGovernmentAgency]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'submit':
            return KYCSubmissionSerializer
        elif self.action in ['update', 'partial_update']:
            return KYCVerificationUpdateSerializer
        return KYCVerificationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_government:
            return KYCVerification.objects.all()
        return KYCVerification.objects.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Update user KYC fields
            for field, value in serializer.validated_data.items():
                setattr(user, field, value)
            user.save()
            
            # Create or update KYC verification record
            kyc, created = KYCVerification.objects.get_or_create(user=user)
            if not created:
                kyc.status = KYCVerification.PENDING
                kyc.rejection_reason = None
                kyc.verified_at = None
                kyc.verified_by = None
            kyc.submitted_at = timezone.now()
            kyc.save()
            
            return Response({"message": "KYC verification submitted successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        if not (request.user.is_admin or request.user.is_government):
            return Response({"detail": "You do not have permission to perform this action."}, 
                            status=status.HTTP_403_FORBIDDEN)
        
        queryset = KYCVerification.objects.filter(status=KYCVerification.PENDING)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)