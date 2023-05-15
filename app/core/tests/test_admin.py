from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):
    """create admin test cases"""

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser("admin@gmail.com", 'admin@123')
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            password='love@123',
            name='Test user'
        )

    def test_users_list(self):
        """test use cases"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_chane(self):
        """test user models with edit fields"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
    def test_user_add(self):
        """test user models for add page"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
