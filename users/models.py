from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as the unique identifier and role-based permissions."""
    
    # Role choices
    ADMIN = 'admin'
    GOVERNMENT = 'government'
    REAL_ESTATE_FIRM = 'real_estate_firm'
    PROPERTY_OWNER = 'property_owner'
    BUYER_RENTER = 'buyer_renter'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (GOVERNMENT, 'Government Agency'),
        (REAL_ESTATE_FIRM, 'Real Estate Firm'),
        (PROPERTY_OWNER, 'Property Owner'),
        (BUYER_RENTER, 'Buyer/Renter'),
    ]
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=BUYER_RENTER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # KYC verification fields
    id_type = models.CharField(max_length=50, blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    id_document = models.FileField(upload_to='id_documents/', blank=True, null=True)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_registration_number = models.CharField(max_length=50, blank=True, null=True)
    business_document = models.FileField(upload_to='business_documents/', blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN
    
    @property
    def is_government(self):
        return self.role == self.GOVERNMENT
    
    @property
    def is_real_estate_firm(self):
        return self.role == self.REAL_ESTATE_FIRM
    
    @property
    def is_property_owner(self):
        return self.role == self.PROPERTY_OWNER
    
    @property
    def is_buyer_renter(self):
        return self.role == self.BUYER_RENTER


class KYCVerification(models.Model):
    """Model for KYC verification requests and status tracking."""
    
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc_verification')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications')
    rejection_reason = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.status}"