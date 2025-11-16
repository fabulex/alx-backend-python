# chats/auth.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email instead of username.
    Treats the 'username' form field as an email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')  # Fallback if using custom forms
        if username is None or password is None:
            return None

        try:
            # Find user by email (case-insensitive)
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            return None  # No fallback needed—no username field

        # Check password and activity
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        # Ensure user is active
        return user.is_active
