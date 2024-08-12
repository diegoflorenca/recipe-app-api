"""
Views for the recipe APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter',
            ),
        ]
    )
)
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

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        """
        We override the `get_queryset` method in the `viewsets.ModelViewSet`
        class to return only the recipes that belong to the authenticated user.
        """
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            # Filtering related fields using the `filter` method
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT,
                enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        """
        Filtering the queryset based on the `assigned_only` parameter.
        If `assigned_only` is True, then we only want to return tags or 
        ingredients that are associated with at least one recipe.
        The `recipe__isnull=False` filter ensures that only tags that 
        have a related recipe are included in the queryset.
        """
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        """
        We override the `get_queryset` method in the `viewsets.GenericViewSet`
        class to return only the tags that belong to the authenticated user.
        """
        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BasicRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BasicRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
