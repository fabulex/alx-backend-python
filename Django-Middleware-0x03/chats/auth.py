# chats/auth.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

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
            logger.warning(f"Failed login attempt for email: {username}")
            return None
        except User.MultipleObjectsReturned:
            logger.error(f"Multiple users found with email: {username}")
            return None

        # Check password and activity
        if user.check_password(password) and self.user_can_authenticate(user):
            logger.info(f"Successful login for user: {user.email}")
            return user

        logger.warning(f"Invalid password for user: {username}")
        return None

    def user_can_authenticate(self, user):
        """
        Ensure user is active
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer to add additional claims to the token.
    """
    username_field = 'email'  # Use email instead of username

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = user.role
        token['user_id'] = str(user.user_id)

        return token

    def validate(self, attrs):
        # Use email for authentication
        data = super().validate(attrs)

        # Add extra user info to response
        data.update({
            'user': {
                'user_id': str(self.user.user_id),
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'role': self.user.role,
            }
        })

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining JWT tokens with email-based authentication.
    """
    serializer_class = CustomTokenObtainPairSerializer
