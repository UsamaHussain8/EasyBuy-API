from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that lets users log in
    using either their username OR email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        try:
            # Try email first
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            try:
                # Fallback to username
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                return None

        # Verify password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
