"""
Serializers for the user API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        # Remove the password from the validated data.
        password = validated_data.pop('password', None)
        # Update the user
        user = super().update(instance, validated_data)

        # If the password is passed, set_password will encrypt the password.
        # save is needed to store the new password in the database.
        if password:
            # set_password will encrypt the password.
            user.set_password(password)
            # save is needed to store the new password in the database.
            user.save()

        return user


# Basic serializer that is used to create a token
# for the user. It is not tight to an specific model.
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        # Input type for password.
        style={'input_type': 'password'},
        # Don't trim whitespaces.
        trim_whitespace=False,
    )

    # Called on the serializer on the validation stage.
    # attrs (attributes) is the validated data from the serializer.
    def validate(self, attrs):
        """Validate and authenticate the user."""
        # retrieve the email from the validated data.
        email = attrs.get('email')
        # retrieve the password from the validated data.
        password = attrs.get('password')
        # Authenticate the user.
        user = authenticate(
            # Get the request from the context.
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        # Check if the user exists.
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(
                msg,
                code='authorization'
            )

        attrs['user'] = user
        return attrs
