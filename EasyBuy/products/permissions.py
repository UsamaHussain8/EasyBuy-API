from rest_framework import permissions

class IsSellerAndOwner(permissions.BasePermission):
    """
    Custom permission: 
    - Only users with role='seller' can perform unsafe actions.
    - A seller can only add/modify/delete their own products.
    """
    def has_permission(self, request, view):
        # SAFE_METHODS = GET, HEAD, OPTIONS — always allowed
        if request.method in permissions.SAFE_METHODS:
            return True

        # not logged in? deny
        if not request.user.is_authenticated:
            return False
        
        # Check if user is authenticated and has a related StoreUser with role 'seller'
        user = request.user

        # user doesn't have a store_user profile? deny
        if not hasattr(user, "store_user"):
            return False

        # allow only if their role is 'seller'
        return user.store_user.role.lower() == "seller" 

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        if not hasattr(request.user, 'store_user') or not hasattr(obj, 'seller'):
            return False
        
        # if not hasattr(obj, 'seller'):
        #     return False
            
        return obj.seller == request.user.store_user