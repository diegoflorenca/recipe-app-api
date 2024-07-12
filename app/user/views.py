"""
Views for the user API.
"""
from rest_framework import (
    generics,
    authentication,
    permissions
)
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


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Manage the authenticated user.

    This view class is used to retrieve and update the
    authenticated user. The view is used to handle HTTP
    GET and PATCH requests.

    Attributes:
        serializer_class (class): The serializer class used to
            serialize the user object.
        authentication_classes (list): The authentication classes
            used to authenticate the user.
        permission_classes (list): The permission classes used to
            check the permissions of the user.

    Methods:
        get_object(): Retrieves and returns the authenticated user.
    """
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retrieves and returns the authenticated user.

        This method retrieves the authenticated user object from
        the request object and returns it. The user object isurl
        obtained by calling the `user` attribute of the request
        object.

        Returns:
            The authenticated user object.
        """
        return self.request.user
