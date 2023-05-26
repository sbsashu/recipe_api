"""test recipe models"""

import tempfile
import os
from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Recipe, Tag, Ingredient
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from decimal import Decimal
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """detail page url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])
def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

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

    def test_recipe_with_new_tags(self):
        """test recipe with tag"""
        payload = {
            'title': 'Recipe 1',
            'time_minutes': 32,
            'price': Decimal('12.3'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
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

    def test_create_recipe_with_existing_tags(self):
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
        recipe = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipe.count(), 1)
        recip = recipe[0]
        self.assertEqual(recip.tags.count(), 2)
        self.assertIn(cr_tag, recip.tags.all())

        for ta in payload['tags']:
            exist = recip.tags.filter(
                 user=self.user,
                 name=ta['name']
            ).exists()
            self.assertTrue(exist)

    def test_tage_update(self):
        """update recipe tags"""
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{'name': 'Lunch'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """test_update_recipe_assign_tag"""
        tag_a = Tag.objects.create(user=self.user, name='Lunch')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_a)

        tag_lun = Tag.objects.create(user=self.user, name='Lunch1')
        payload = {'tags': [{'name': 'Lunch1'}]}
        uri = detail_url(recipe.id)
        res = self.client.patch(uri, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(tag_a, recipe.tags.all())
        self.assertIn(tag_lun, recipe.tags.all())

    def test_clear_tags(self):
        """clear tags from recipe"""
        tag = Tag.objects.create(user=self.user, name='Lunch')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        uri = detail_url(recipe.id)
        payload = {'tags': []}
        res = self.client.patch(uri, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_ingredient_with_recipe(self):
        """test create ingredient with recipe"""
        payload = {
            'title': 'Name ingredient',
            'time_minutes': 30,
            'price': Decimal('12.21'),
            'ingredients': [{'name': 'Ingredient1'}, {'name': 'Ingredient2'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=ingredient['name']
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_user(self):
        """test create recipe with existing user"""
        ingre = Ingredient.objects.create(user=self.user, name='Ingr1')
        payload = {
            'title': 'Munchorian',
            'time_minutes': 30,
            'price': Decimal('12.12'),
            'ingredients': [{'name': 'Ingr1'}, {'name': 'Ingre2'}]
        }

        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingre, recipe.ingredients.all())

        for ingred in payload['ingredients']:
            exists = recipe.ingredients.filter(
                user=self.user,
                name=ingred['name']
            ).exists()
            self.assertTrue(exists)
    def test_upate_on_ingredient(self):
        """test update on ingredient"""
        recipe = create_recipe(user=self.user)

        payload = {
            'ingredients': [{'name': 'Liquid'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingr = Ingredient.objects.get(user=self.user, name='Liquid')
        self.assertIn(new_ingr, recipe.ingredients.all())

    def test_update_recipe_ingredient(self):
        """test_update_recipe_ingredient"""
        ingre1 = Ingredient.objects.create(user=self.user, name='Peper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingre1)
        ingre2 = Ingredient.objects.create(user=self.user, name='Chilli')
        payload = {
            'ingredients': [{'name': 'Chilli'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingre2, recipe.ingredients.all())
        self.assertNotIn(ingre1, recipe.ingredients.all())

    def test_recipe_from_ingredients(self):
        """test update igredients"""
        recipe = create_recipe(user=self.user)
        ingre = Ingredient.objects.create(user=self.user, name='chilli')
        recipe.ingredients.add(ingre)

        payload = {
            'ingredients': []
        }
        res = self.client.patch(detail_url(recipe.id), payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """test flter by tags"""
        r1 = create_recipe(user=self.user, title='Thai vegeterian curry')
        r2 = create_recipe(user=self.user, title='Aubergine with tahini')
        tag1 = Tag.objects.create(user=self.user, name="Vegan")
        tag2 = Tag.objects.create(user=self.user, name="Vegiterain")
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title='Fish and chips')
        params = {'tags': f'{tag1.id},{tag2.id}'}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

    def test_filter_by_ingredients(self):
        """test filter by ingredients"""
        r1 = create_recipe(user=self.user, title='samosa with onion')
        r2 = create_recipe(user=self.user, title='namkin with onion')
        ing1 = Ingredient.objects.create(user=self.user, name='Oil')
        ing2 = Ingredient.objects.create(user=self.user, name='Namkin')
        r1.ingredients.add(ing1)
        r2.ingredients.add(ing2)

        r3 = create_recipe(user=self.user, title='Momos')
        params = {'ingredients': f'{ing1.id}, {ing2.id}'}
        res = self.client.get(RECIPE_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)

        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)

class ImageUploadTestCase(TestCase):
    """image upload test cases """

    def setUp(self):
        """authenticate user"""
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='testimage@gmail.com', password='test@123456')
        self.client.force_authenticate(user=self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """upload test case"""
        url = image_upload_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as filepath:
            img = Image.new('RGB', (10, 10))
            img.save(filepath, format='JPEG')
            filepath.seek(0)
            payload = {'image': filepath}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_bad_image_file(self):
        """bad image file"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'nofileimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
