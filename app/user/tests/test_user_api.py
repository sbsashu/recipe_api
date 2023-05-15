"""test cases for user apis"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

CREATE_USER_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')
ME_USER = reverse('user:me')

def create_user(**wargs):
    """create user function"""
    return get_user_model().objects.create_user(**wargs)

class PublicAPITests(TestCase):
    """test case to check public request"""

    def setUp(self):
        self.client = APIClient()

    def test_user_creation_with_successfull(self):
        """create user with success message"""
        payload = {
            'email': 'test12@gmail.com',
            'password': 'ashu@12345',
            'name': 'testuser',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_creation_with_existing_user(self):
        """test existing user"""
        payload = {
            'email': 'test12@gmail.com',
            'password': 'ashu@12345',
            'name': 'testuser',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_for_short_password(self):
        """test user to check too short password"""
        payload = {
            'email': 'test32@gmail.com',
            'password': 'as',
            'name': 'Testuser1'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user)

    def test_authenticate_user_with_token(self):
        """test authentication with token"""

        payload = {
            'name':'Test user',
            'email': 'testuser1@gmail.com',
            'password': 'ashu@123445',
        }
        create_user(**payload)
        user_detail = {
            'email': 'testuser1@gmail.com',
            'password': 'ashu@123445',
        }
        res = self.client.post(CREATE_TOKEN_URL, user_detail)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_authenticate_user_token_error(self):
        """error token with error"""
        payload = {
            'email': 'testuser12@gmail.com',
            'password': 'goodpass',
        }
        create_user(**payload)
        user_detail = {'email': 'testuser12@gmail.com','password': 'badpass'}
        res = self.client.post(CREATE_TOKEN_URL, user_detail)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticate_user_token_without_password_error(self):
        """without password with error request"""
        payload = {
            'email': 'testuser13@gmail.com',
            'password': 'goodpass@',
            'name': 'Test user',
        }
        create_user(**payload)
        user_details = {
            'email': '',
            'password': 'goodpass@'
        }
        res = self.client.post(CREATE_TOKEN_URL, user_details)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_authenticate_user(self):
        """authicate public user"""
        res = self.client.get(ME_USER)

class PrivateUserUserApiTests(TestCase):
    """Test api request that's require authentication."""

    def setUp(self):
        self.user = create_user(
            email='testabcd@gmail.com',
            password='asasjkds',
            name='Test user',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_user_profile(self):
        """retrive user profile data"""
        res = self.client.get(ME_USER)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertEqual(res.data, {'email': self.user.email, 'password': self.user.password})

    def test_method_me_not_allowed(self):
        """method not allowed"""
        res = self.client.post(ME_USER, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """update user profile"""
        payload = {
            'name': 'udated name',
            'password': 'updatedpass123',
        }
        res = self.client.patch(ME_USER, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)