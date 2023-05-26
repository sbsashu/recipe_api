"""
test ingredient test api
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
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

    def test_assinged_ingredient_to_recipe(self):
        """Test assinged ingredient to recipe filter"""
        ng1 = Ingredient.objects.create(user=self.user, name="Mirchi")
        ng2 = Ingredient.objects.create(user=self.user, name="Mirchi1")
        r1 = Recipe.objects.create(user=self.user, title='Burger', time_minutes=30, price=Decimal('12.12'))

        r1.ingredients.add(ng1)
        res = self.client.get(INGRIDIENT_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        s1 = IngredientSerializer(ng1)
        s2 = IngredientSerializer(ng2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_unique(self):
        """test filter unique ingredient"""
        ng = Ingredient.objects.create(user=self.user, name="Eggs")
        Ingredient.objects.create(user=self.user, name="Curry")

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Mix',
            price=Decimal('12.13'),
            time_minutes=21
        )

        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Mix1',
            price=Decimal('12.13'),
            time_minutes=21
        )

        recipe1.ingredients.add(ng)
        recipe2.ingredients.add(ng)

        res = self.client.get(INGRIDIENT_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)