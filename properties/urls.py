from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import (
    PropertyViewSet, PropertyImageViewSet, PropertyDocumentViewSet,
    AmenityViewSet, LocationViewSet
)

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'amenities', AmenityViewSet)
router.register(r'locations', LocationViewSet)

# Nested routes for property images and documents
property_router = routers.NestedSimpleRouter(router, r'properties', lookup='property')
property_router.register(r'images', PropertyImageViewSet, basename='property-images')
property_router.register(r'documents', PropertyDocumentViewSet, basename='property-documents')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(property_router.urls)),
]