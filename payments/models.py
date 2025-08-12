from django.db import models
from django.utils import timezone
from properties.models import Property
from users.models import User


class Payment(models.Model):
    """Model for tracking payments for properties."""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]
    
    PAYSTACK = 'paystack'
    FLUTTERWAVE = 'flutterwave'
    BANK_TRANSFER = 'bank_transfer'
    
    PAYMENT_METHOD_CHOICES = [
        (PAYSTACK, 'Paystack'),
        (FLUTTERWAVE, 'Flutterwave'),
        (BANK_TRANSFER, 'Bank Transfer'),
    ]
    
    RENT = 'rent'
    PURCHASE = 'purchase'
    DEPOSIT = 'deposit'
    COMMISSION = 'commission'
    
    PAYMENT_TYPE_CHOICES = [
        (RENT, 'Rent'),
        (PURCHASE, 'Purchase'),
        (DEPOSIT, 'Deposit'),
        (COMMISSION, 'Commission'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_made')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    reference = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.payment_type} payment for {self.property.title} - {self.status}"
    
    def save(self, *args, **kwargs):
        if self.status == self.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Model for tracking transaction details and history."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50)  # e.g., 'payment', 'refund', 'verification'
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)  # e.g., 'success', 'failed', 'pending'
    gateway_response = models.TextField(blank=True, null=True)  # Response from payment gateway
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.status} - {self.created_at}"


class Invoice(models.Model):
    """Model for generating invoices for property transactions."""
    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (OVERDUE, 'Overdue'),
        (CANCELLED, 'Cancelled'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='invoices')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.status}"
    
    def is_overdue(self):
        return self.status == self.PENDING and self.due_date < timezone.now().date()
    
    def save(self, *args, **kwargs):
        if self.is_overdue() and self.status == self.PENDING:
            self.status = self.OVERDUE
        super().save(*args, **kwargs)


class PaymentPlan(models.Model):
    """Model for defining payment plans for properties."""
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    BIANNUALLY = 'biannually'
    ANNUALLY = 'annually'
    ONE_TIME = 'one_time'
    
    FREQUENCY_CHOICES = [
        (MONTHLY, 'Monthly'),
        (QUARTERLY, 'Quarterly'),
        (BIANNUALLY, 'Biannually'),
        (ANNUALLY, 'Annually'),
        (ONE_TIME, 'One Time'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payment_plans')
    name = models.CharField(max_length=100)
    description = models.TextField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_months = models.PositiveIntegerField(default=12)  # Total duration in months
    initial_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # e.g., 30% down payment
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.property.title}"


class Subscription(models.Model):
    """Model for tracking user subscriptions to payment plans."""
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (CANCELLED, 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.payment_plan.name} - {self.status}"
    
    def is_expired(self):
        return self.end_date < timezone.now().date()
    
    def save(self, *args, **kwargs):
        if self.is_expired() and self.status == self.ACTIVE:
            self.status = self.EXPIRED
        super().save(*args, **kwargs)