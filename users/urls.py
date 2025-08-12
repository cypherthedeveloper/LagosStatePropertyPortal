from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserViewSet, KYCVerificationViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'kyc', KYCVerificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]