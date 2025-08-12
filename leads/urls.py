from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import LeadViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='leads')

# Nested routes for messages within leads
lead_router = routers.NestedSimpleRouter(router, r'leads', lookup='lead')
lead_router.register(r'messages', MessageViewSet, basename='lead-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(lead_router.urls)),
]