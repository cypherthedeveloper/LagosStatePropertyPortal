from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet,
    TransactionViewSet,
    InvoiceViewSet,
    PaymentPlanViewSet,
    SubscriptionViewSet
)

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'payment-plans', PaymentPlanViewSet)
router.register(r'subscriptions', SubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]