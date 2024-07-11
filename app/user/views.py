"""
Views for the user API.
"""
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    # Custom serializer for the token because
    # we use the email as the username.
    serializer_class = AuthTokenSerializer
    # Set the renderer classes to the default ones. This allows
    # the token endpoint to return the token in the same format
    # as the browsable API.
    # The default renderer classes are configured in the
    # `REST_FRAMEWORK` setting in settings.py.
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
