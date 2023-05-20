"""
test ingredient test api
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGRIDIENT_URL = reverse('recipe:ingredient-list')

def detail_uri(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])

def create_user(email="exmaple@gmail.com", password="abcde@123444"):
    return get_user_model().objects.create_user(email, password)

class PublicIngidientTest(TestCase):
    """unauthenticated user apis test cases"""

    def setUp(self):
        self.client = APIClient()

    def test_ingridient_list(self):
        """test ingridient list"""
        res = self.client.get(INGRIDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngridientTest(TestCase):
    """authenticated user apis test cases"""
    def setUp(self):
        """authenticate user"""
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_ingridient_list(self):
        """get ingrigient list"""
        Ingredient.objects.create(user=self.user, name="Patato")
        Ingredient.objects.create(user=self.user, name="Onion")
        res = self.client.get(INGRIDIENT_URL)

        ingr = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingr, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_ingridient_for_correct_user(self):
        """get for correct mapped user"""
        user = create_user(email="exmapl1@gmail.com")
        Ingredient.objects.create(user=user, name='Lunch box')
        ingridient = Ingredient.objects.create(user=self.user, name="New oil")
        res = self.client.get(INGRIDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingridient.name)
        self.assertEqual(res.data[0]['id'], ingridient.id)

    def test_ingredient_upate(self):
        """upate ingredient data"""
        ingredient = Ingredient.objects.create(user=self.user, name='YYYY')
        payload = {'name': 'XXXX'}
        uri = detail_uri(ingredient.id)
        res = self.client.patch(uri, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_ingredient_delete(self):
        """delete ingredient data"""
        ingredient = Ingredient.objects.create(user=self.user, name='YYYY')
        uri = detail_uri(ingredient.id)
        res = self.client.delete(uri)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingre = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingre.exists())