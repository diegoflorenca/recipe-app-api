"""
Views for the recipe APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
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
        # Custom action for uploading an image
        if self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasicRecipeAttrViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Manage basic recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        """
        We override the `get_queryset` method in the `viewsets.GenericViewSet`
        class to return only the tags that belong to the authenticated user.
        """
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BasicRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BasicRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
