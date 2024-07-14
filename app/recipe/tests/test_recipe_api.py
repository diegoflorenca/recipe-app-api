"""
Test for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    """Create and return a sample recipe."""
    """
    Create a default recipe object so we don't have to
    create one manually for each test. We can simply overwrite
    any of the attributes we want to change.
    """
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf'
    }
    """"
    We can use the **params argument to unpack the dictionary
    and pass each key-value pair as an argument to the create
    function, in order to override the default values.
    """
    defaults.update(params)

    """
    Create the recipe object using the defaults dictionary
    and the user object that was passed in as an argument.
    Then save it in the database and return it.
    """
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        """
        Return the list of recipes in the response data in the
        same order as they were created in the database.
        The most recent recipe will be first in the list because
        of the '-id' ordering returns the recipes in descending
        order.
        """
        recipes = Recipe.objects.all().order_by('-id')
        """
        We are using the serializer to serialize the recipes and
        compare them to the response data. Therefore, we can
        that the response data matches the serializer data.
        The many=True argument tells the serializer to serialize
        a list of objects instead of a single object.
        """
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Assert that the response data matches the serializer data
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""

        # Create a new user that will not be authenticated.
        other_user = get_user_model().objects.create_user(
            'otheruser@example.com',
            'password123',
        )

        # Create a new recipe for the other user (not authenticated).
        create_recipe(user=other_user)
        # Create a new recipe for the authenticated user.
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        # Get the list of recipes for the authenticated user.
        recipes = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
