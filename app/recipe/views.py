"""
Views for the recipe APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    # Define the serializer class for the RecipeViewSet.
    serializer_class = serializers.RecipeDetailSerializer
    # Set the queryset to retrieve all recipes for the authenticated user.
    queryset = Recipe.objects.all()
    """
    Set the authentication class for the RecipeViewSet.
    The `TokenAuthentication` class is used to authenticate
    the user using a token. The token is obtained when the user
    logs in and is included in the request header.
    """
    authentication_classes = [TokenAuthentication]
    """
    Set the permission class for the RecipeViewSet.
    The `IsAuthenticated` class is used to ensure that the user
    is authenticated before accessing any recipe data.
    """
    permission_classes = [IsAuthenticated]
    """
    Therefor, the user must have a token in the request header and
    be authenticated to access recipe data.
    """

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        """
        We override the `get_queryset` method in the `viewsets.ModelViewSet`
        class to return only the recipes that belong to the authenticated user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)


class TagViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        """
        We override the `get_queryset` method in the `viewsets.GenericViewSet`
        class to return only the tags that belong to the authenticated user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        """
        We override the `get_queryset` method in the `viewsets.GenericViewSet`
        class to return only the ingredients that belong to the authenticated
        user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')
