from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ComplianceReport, PropertyCompliance, ComplianceRequirement, PropertyRequirementCheck
from .serializers import (
    ComplianceReportSerializer, 
    PropertyComplianceSerializer, 
    ComplianceRequirementSerializer,
    PropertyRequirementCheckSerializer
)
from permissions import IsAdmin, IsGovernmentAgency, IsPropertyOwnerOrReadOnly
from properties.models import Property


class ComplianceRequirementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing compliance requirements."""
    queryset = ComplianceRequirement.objects.all()
    serializer_class = ComplianceRequirementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    
    def get_permissions(self):
        """Only government agencies and admins can create, update, or delete requirements."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & (IsGovernmentAgency | IsAdmin)]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class PropertyComplianceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing property compliance."""
    queryset = PropertyCompliance.objects.all()
    serializer_class = PropertyComplianceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['compliance_status', 'property__owner']
    search_fields = ['property__title', 'notes']
    ordering_fields = ['reviewed_at', 'last_inspection_date', 'next_inspection_date']
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated & (IsGovernmentAgency | IsAdmin)]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated & IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = PropertyCompliance.objects.all()
        
        if user.is_staff or user.role == user.GOVERNMENT:
            return queryset
        elif user.role in [user.PROPERTY_OWNER, user.REAL_ESTATE_FIRM]:
            return queryset.filter(property__owner=user)
        else:
            return queryset.filter(property__verification_status=Property.VERIFIED)
    
    @action(detail=False, methods=['get'])
    def my_properties(self, request):
        """Get compliance status for properties owned by the current user."""
        queryset = self.get_queryset().filter(property__owner=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def non_compliant(self, request):
        """Get all non-compliant properties."""
        if not (request.user.is_staff or request.user.role == request.user.GOVERNMENT):
            return Response(
                {"detail": "You do not have permission to perform this action."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(compliance_status=PropertyCompliance.NON_COMPLIANT)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PropertyRequirementCheckViewSet(viewsets.ModelViewSet):
    """ViewSet for managing property requirement checks."""
    queryset = PropertyRequirementCheck.objects.all()
    serializer_class = PropertyRequirementCheckSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'property_compliance', 'requirement']
    ordering_fields = ['checked_at']
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated & (IsGovernmentAgency | IsAdmin)]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated & IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = PropertyRequirementCheck.objects.all()
        
        if user.is_staff or user.role == user.GOVERNMENT:
            return queryset
        elif user.role in [user.PROPERTY_OWNER, user.REAL_ESTATE_FIRM]:
            return queryset.filter(property_compliance__property__owner=user)
        else:
            return queryset.filter(property_compliance__property__verification_status=Property.VERIFIED)


class ComplianceReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing compliance reports."""
    queryset = ComplianceReport.objects.all()
    serializer_class = ComplianceReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'generated_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated & (IsGovernmentAgency | IsAdmin)]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = ComplianceReport.objects.all()
        
        if user.is_staff or user.role == user.GOVERNMENT:
            return queryset
        elif user.role in [user.PROPERTY_OWNER, user.REAL_ESTATE_FIRM]:
            # Property owners can only see approved reports
            return queryset.filter(status=ComplianceReport.APPROVED)
        else:
            # Buyers/renters can only see approved reports
            return queryset.filter(status=ComplianceReport.APPROVED)
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """Get reports generated by the current user."""
        if not (request.user.is_staff or request.user.role == request.user.GOVERNMENT):
            return Response(
                {"detail": "You do not have permission to perform this action."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(generated_by=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)