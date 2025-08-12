from rest_framework import serializers
from .models import Payment, Transaction, Invoice, PaymentPlan, Subscription
from properties.serializers import PropertyListSerializer
from users.serializers import UserSerializer


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction details."""
    class Meta:
        model = Transaction
        fields = ['id', 'payment', 'transaction_type', 'amount', 'status', 
                  'gateway_response', 'created_at']
        read_only_fields = ['created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment details."""
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='property',
        queryset=Payment.objects.all()
    )
    payer = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'property', 'property_id', 'payer', 'receiver', 
                  'amount', 'payment_type', 'payment_method', 'transaction_id', 
                  'reference', 'status', 'created_at', 'updated_at', 
                  'completed_at', 'transactions']
        read_only_fields = ['created_at', 'updated_at', 'completed_at', 'payer', 'receiver']
    
    def create(self, validated_data):
        # Set payer to current user
        validated_data['payer'] = self.context['request'].user
        # Set receiver to property owner
        validated_data['receiver'] = validated_data['property'].owner
        return super().create(validated_data)


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoice details."""
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='property',
        queryset=Invoice.objects.all()
    )
    user = UserSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True, source='is_overdue')
    
    class Meta:
        model = Invoice
        fields = ['id', 'property', 'property_id', 'user', 'payment', 
                  'invoice_number', 'amount', 'description', 'status', 
                  'due_date', 'created_at', 'updated_at', 'is_overdue']
        read_only_fields = ['created_at', 'updated_at', 'user', 'payment']
    
    def create(self, validated_data):
        # Set user to current user if creating an invoice for a buyer
        # or to property owner if admin is creating it
        request_user = self.context['request'].user
        if request_user.is_staff or request_user.role in [request_user.GOVERNMENT, request_user.REAL_ESTATE_FIRM, request_user.PROPERTY_OWNER]:
            # Admin or property owner creating invoice for a buyer
            user_id = self.context['request'].data.get('user_id')
            if user_id:
                from users.models import User
                try:
                    validated_data['user'] = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"user_id": "User does not exist"})
            else:
                raise serializers.ValidationError({"user_id": "User ID is required"})
        else:
            # Buyer creating invoice for themselves
            validated_data['user'] = request_user
        
        # Generate invoice number
        import uuid
        validated_data['invoice_number'] = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        return super().create(validated_data)


class PaymentPlanSerializer(serializers.ModelSerializer):
    """Serializer for payment plan details."""
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='property',
        queryset=PaymentPlan.objects.all()
    )
    
    class Meta:
        model = PaymentPlan
        fields = ['id', 'property', 'property_id', 'name', 'description', 
                  'frequency', 'duration_months', 'initial_payment_percentage', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        # Ensure only property owner can create payment plans
        request_user = self.context['request'].user
        property_instance = data.get('property')
        
        if property_instance and property_instance.owner != request_user and not request_user.is_staff:
            raise serializers.ValidationError("You can only create payment plans for your own properties")
        
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscription details."""
    user = UserSerializer(read_only=True)
    payment_plan = PaymentPlanSerializer(read_only=True)
    payment_plan_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='payment_plan',
        queryset=Subscription.objects.all()
    )
    is_expired = serializers.BooleanField(read_only=True, source='is_expired')
    
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'payment_plan', 'payment_plan_id', 'start_date', 
                  'end_date', 'status', 'created_at', 'updated_at', 'is_expired']
        read_only_fields = ['created_at', 'updated_at', 'user']
    
    def create(self, validated_data):
        # Set user to current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)