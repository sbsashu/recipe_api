"""
Creating test cases to test tag apis
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from django.test import TestCase

TAG_URL = reverse('recipe:tag-list')

def patch_url(id):
    return reverse('recipe:tag-detail', args=[id])

def create_user(email="user@exmple.com", password="password"):
    """create test user"""
    return get_user_model().objects.create_user(email, password)

class PublicTagTestCase(TestCase):
    """Tag test case for unauthenticate user"""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user(self):
        """test case for unauthenticated user"""
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagTestCase(TestCase):
    """test case for authenticated user"""
    def setUp(self):
        self.client = APIClient()
        self.user  = create_user()
        self.client.force_authenticate(user= self.user)

    def test_tag_get_list(self):
        """test tag get list"""

        Tag.objects.create(user=self.user, name="tag")
        Tag.objects.create(user=self.user, name="tag1")
        Tag.objects.create(user=self.user, name="tag2")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tag_limit_user(self):
        """tag with limit user"""

        user1 = create_user(email="abcd@gmail.com")
        Tag.objects.create(user=user1, name="tag2")
        tag = Tag.objects.create(user=self.user, name="tag3")
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag_for_authenticated_user(self):
        """tag with limit user"""
        tag = Tag.objects.create(user=self.user, name="tag3")
        payload = {
            'name': 'tag2'
        }
        get_patch_url = patch_url(tag.id)
        res = self.client.patch(get_patch_url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tags(self):
        """detete tags details"""
        tag = Tag.objects.create(user=self.user, name="Tags")
        url_id = patch_url(tag.id)
        res = self.client.delete(url_id)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_assinged_tags_to_recipe(self):
        """Test assinged tags to recipe filter"""
        tag1 = Tag.objects.create(user=self.user, name="Mirchi")
        tag2 = Tag.objects.create(user=self.user, name="Mirchi1")
        r1 = Recipe.objects.create(user=self.user, title='Burger', time_minutes=30, price=Decimal('12.12'))

        r1.tags.add(tag1)
        res = self.client.get(TAG_URL, {'assigned_only': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_unique(self):
        """test filter unique ingredient"""
        ng = Tag.objects.create(user=self.user, name="Eggs")
        Tag.objects.create(user=self.user, name="Curry")

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

        recipe1.tags.add(ng)
        recipe2.tags.add(ng)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)