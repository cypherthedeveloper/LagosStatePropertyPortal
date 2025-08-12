from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission to only allow admin users to access the view."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsGovernmentAgency(permissions.BasePermission):
    """Permission to only allow government agency users to access the view."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_government


class IsRealEstateFirm(permissions.BasePermission):
    """Permission to only allow real estate firm users to access the view."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_real_estate_firm


class IsPropertyOwner(permissions.BasePermission):
    """Permission to only allow property owner users to access the view."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_property_owner


class IsBuyerRenter(permissions.BasePermission):
    """Permission to only allow buyer/renter users to access the view."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_buyer_renter


class IsVerifiedUser(permissions.BasePermission):
    """Permission to only allow verified users to access the view."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_verified


class IsPropertyOwnerOrRealEstateFirm(permissions.BasePermission):
    """Permission to only allow property owners or real estate firms to access the view."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_property_owner or request.user.is_real_estate_firm)


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission to only allow owners of an object or admin users to edit it."""
    
    def has_object_permission(self, request, view, obj):
        # Allow admin users
        if request.user.is_admin:
            return True
        
        # Check if the object has an owner field
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsPropertyOwnerOrReadOnly(permissions.BasePermission):
    """Permission to only allow property owners to edit their properties."""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.owner == request.user