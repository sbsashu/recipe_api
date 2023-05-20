"""
Tests for models
"""
from decimal import Decimal
from core import models
from django.test import TestCase
from django.contrib.auth import get_user_model

def create_user(email="user@example.com", password="ashut123"):
    """creating user for model test"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """user creation test"""

    def test_create_user_with_email_successfully(self):
        """test create user with successfully"""
        email="testuser@gmail.com"
        password="ashu@123"

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_new_user(self):
        """Create new user created for auth"""
        sample_emails = [
            ['test@gmail.com', 'test@gmail.com'],
            ['test123@gmail.com', 'test123@gmail.com'],
            ['Test13@gmail.COM', 'Test13@gmail.com'],
            ['Test@GMAIL.COM', 'Test@gmail.com'],
        ]

        for email, expected_email in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample@123')
            self.assertEqual(user.email, expected_email)

    def test_create_new_user_without_email(self):
        """create user without email that raise value errors"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'asas@123')

    def test_create_super(self):
        """create super user test case"""

        user = get_user_model().objects.create_superuser("tes@gmail.com", "ashu@123")

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)

    def test_recipe_with_user_model(self):
        """create recipe with user"""
        user = get_user_model().objects.create_user(
            email='test12@gmail.com',
            password='testuser13',
            name='Test user',
        )
        res = models.Recipe.objects.create(
            user=user,
            title='Test recipe models',
            price=Decimal('5.40'),
            description='Recipe is described with energy',
            time_minutes=5,
        )
        self.assertEqual(str(res), res.title)

    def test_tag_model(self):
        """tag test"""
        user = create_user()
        tag = models.Tag(
            user=user,
            name= "tag name",
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredianent_model(self):
        """tag test"""
        user = create_user()
        in_gre = models.Ingredient(
            user=user,
            name= "ingrediant name",
        )
        self.assertEqual(str(in_gre), in_gre.name)