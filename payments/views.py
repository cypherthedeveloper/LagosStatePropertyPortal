from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Payment, Transaction, Invoice, PaymentPlan, Subscription
from .serializers import (
    PaymentSerializer, 
    TransactionSerializer, 
    InvoiceSerializer,
    PaymentPlanSerializer,
    SubscriptionSerializer
)
from permissions import IsAdmin, IsVerifiedUser, IsOwnerOrAdmin
from django.utils import timezone
import uuid


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_type', 'payment_method', 'property']
    ordering_fields = ['created_at', 'amount']
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated & IsVerifiedUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = Payment.objects.all()
        
        if user.is_staff:
            return queryset
        else:
            # Users can see payments they made or received
            return queryset.filter(payer=user) | queryset.filter(receiver=user)
    
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Get payments made by the current user."""
        queryset = self.get_queryset().filter(payer=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received_payments(self, request):
        """Get payments received by the current user."""
        queryset = self.get_queryset().filter(receiver=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        """Verify a payment and update its status."""
        payment = self.get_object()
        
        # In a real implementation, this would verify with the payment gateway
        # For now, we'll just update the status
        payment.status = Payment.COMPLETED
        payment.completed_at = timezone.now()
        payment.save()
        
        # Create a transaction record
        Transaction.objects.create(
            payment=payment,
            transaction_type='verification',
            amount=payment.amount,
            status='success',
            gateway_response='Payment verified successfully'
        )
        
        # If there's an invoice associated with this payment, update it
        try:
            invoice = payment.invoice
            invoice.status = Invoice.PAID
            invoice.save()
        except Invoice.DoesNotExist:
            pass
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing transactions (read-only)."""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment', 'transaction_type', 'status']
    ordering_fields = ['created_at', 'amount']
    
    def get_permissions(self):
        """Only authenticated users can view transactions."""
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = Transaction.objects.all()
        
        if user.is_staff:
            return queryset
        else:
            # Users can see transactions for payments they made or received
            return queryset.filter(payment__payer=user) | queryset.filter(payment__receiver=user)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invoices."""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'property', 'user']
    ordering_fields = ['created_at', 'due_date', 'amount']
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action == 'create':
            # Property owners, real estate firms, and admins can create invoices
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = Invoice.objects.all()
        
        if user.is_staff:
            return queryset
        elif user.role in [user.PROPERTY_OWNER, user.REAL_ESTATE_FIRM]:
            # Property owners can see invoices for their properties
            return queryset.filter(property__owner=user)
        else:
            # Buyers/renters can see their own invoices
            return queryset.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def generate_payment(self, request, pk=None):
        """Generate a payment for an invoice."""
        invoice = self.get_object()
        
        # Check if invoice already has a payment
        if invoice.payment:
            return Response(
                {"detail": "This invoice already has a payment associated with it."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get payment method from request
        payment_method = request.data.get('payment_method')
        if not payment_method:
            return Response(
                {"detail": "Payment method is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create payment
        payment = Payment.objects.create(
            property=invoice.property,
            payer=invoice.user,
            receiver=invoice.property.owner,
            amount=invoice.amount,
            payment_type=Payment.RENT if invoice.property.listing_type == 'for_rent' else Payment.PURCHASE,
            payment_method=payment_method,
            reference=f"PAY-{uuid.uuid4().hex[:8].upper()}",
            status=Payment.PENDING
        )
        
        # Link payment to invoice
        invoice.payment = payment
        invoice.save()
        
        # Return payment details
        payment_serializer = PaymentSerializer(payment)
        return Response(payment_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue invoices."""
        queryset = self.get_queryset().filter(status=Invoice.OVERDUE)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PaymentPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment plans."""
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'frequency', 'is_active']
    ordering_fields = ['created_at', 'duration_months']
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only property owners and admins can manage payment plans
            permission_classes = [permissions.IsAuthenticated & IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = PaymentPlan.objects.all()
        
        if user.is_staff:
            return queryset
        elif user.role in [user.PROPERTY_OWNER, user.REAL_ESTATE_FIRM]:
            # Property owners can see payment plans for their properties
            return queryset.filter(property__owner=user)
        else:
            # Buyers/renters can see active payment plans for verified properties
            from properties.models import Property
            return queryset.filter(
                is_active=True, 
                property__verification_status=Property.VERIFIED
            )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscriptions."""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_plan', 'status']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    
    def get_permissions(self):
        """Define permissions based on action."""
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated & IsVerifiedUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated & IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = Subscription.objects.all()
        
        if user.is_staff:
            return queryset
        elif user.role in [user.PROPERTY_OWNER, user.REAL_ESTATE_FIRM]:
            # Property owners can see subscriptions for their payment plans
            return queryset.filter(payment_plan__property__owner=user)
        else:
            # Buyers/renters can see their own subscriptions
            return queryset.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active subscriptions for the current user."""
        queryset = self.get_queryset().filter(status=Subscription.ACTIVE, user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)