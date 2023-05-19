"""test recipe models"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Recipe, Tag
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from decimal import Decimal
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """detail page url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """create recipe data"""
    defaults = {
        'title': 'Test recipe',
        'description': 'Test recipe description',
        'link': 'https://test/love.pdf',
        'price': Decimal('5.55'),
        'time_minutes': 5,
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeTests(TestCase):
    """public recipe test case"""

    def setUp(self):
        self.cleint = APIClient()

    def test_authenticate_required(self):
        """public authenicate required"""
        res = self.cleint.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeTests(TestCase):
    """private recipe test cases"""

    def setUp(self):
        """authenticate user"""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'pass@123',
        )
        self.client.force_authenticate(self.user)

    def test_authenticate_create_recipe(self):
        """create recipe with authenticate user"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe_list_limited_user(self):
        """test recipe list limited user"""
        other_user = get_user_model().objects.create_user(
            'api@gmail.com',
            'passs@12222',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_recipe_detail(self):
        """detail serializer"""
        recipe = create_recipe(user=self.user)
        res = self.client.get(detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating apis"""
        payload = {
            'title': 'recipe 1',
            'time_minutes': 30,
            'price': Decimal('23.23'),
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_paritial_update(self):
        """update paritail update"""
        orignal_link = "https://exmaple.com/a.pdf"
        recipe = create_recipe(
            link=orignal_link,
            title="Test link",
            user=self.user,
        )
        payload = {'title': 'Sample tickets'}
        detail = detail_url(recipe.id)
        res = self.client.patch(detail, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, orignal_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """update full payload"""
        recipe = create_recipe(
            user=self.user,
            title="sample test title",
            link="https://example.com/ed.pdf",
            price=Decimal('23.33'),
            time_minutes=23
         )
        payload = {
            'user':self.user,
            'title':"recipe user",
            'link':"https://examasdple.com/ed.pdf",
            'price':Decimal('23.22'),
            'time_minutes':34
        }
        detail_uri = detail_url(recipe.id)
        res = self.client.put(detail_uri, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """delete recipe"""
        recipe = create_recipe(user=self.user)
        recipe_uri = detail_url(recipe.id)
        res = self.client.delete(recipe_uri)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_recipe_with_error(self):
        """delete recipe"""
        user = get_user_model().objects.create_user(email='testuser@gmail.com', password="testuser")
        recipe = create_recipe(user=user)
        recipe_uri = detail_url(recipe.id)
        payload = {'user': user.id}
        res = self.client.patch(recipe_uri, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, recipe.user)

    def test_delete_recipe_from_other_user_error(self):
        """test_delete_recipe_from_other_user_error"""
        user = get_user_model().objects.create_user(email="testuser@gmail.com", password="testuser@123")
        recipe = create_recipe(user=user)
        recipe_uri = detail_url(recipe.id)
        res = self.client.delete(recipe_uri)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_with_tag(self):
        """test recipe with tag"""
        payload = {
            'title': 'Recipe 1',
            'time_minutes': 32,
            'price': Decimal('12.3'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)
        recipe = recipe[0]
        self.assertEqual(recipe.tags.count(), 2)
        for elm in payload['tags']:
            exist = recipe.tags.filter(
                name=elm['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exist)

    def test_create_recipe_with_tag(self):
        """test create recipe tag"""
        cr_tag = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Recipe 2',
            'time_minutes': 30,
            'price': Decimal('12.32'),
            'tags': [{'name': 'Indian'}, {'name': 'Soda Pani'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.create(user=self.user)
        self.assertEqual(recipe.count(), 1)
        recip = recipe[0]
        self.assertIn(cr_tag, recip.tags.all())

        self.assertEqual(recip.tags.count(), 2)

        for ta in payload['tags']:
            exist = recip.filter.filter(
                 user=self.user,
                 name=ta['name']
            ).exists()
            self.assertIn(exist)
