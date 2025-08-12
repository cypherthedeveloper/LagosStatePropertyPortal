from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComplianceReportViewSet,
    PropertyComplianceViewSet,
    ComplianceRequirementViewSet,
    PropertyRequirementCheckViewSet
)

router = DefaultRouter()
router.register(r'reports', ComplianceReportViewSet)
router.register(r'property-compliance', PropertyComplianceViewSet)
router.register(r'requirements', ComplianceRequirementViewSet)
router.register(r'requirement-checks', PropertyRequirementCheckViewSet)

urlpatterns = [
    path('', include(router.urls)),
]