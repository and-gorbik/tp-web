from qa import models
from django.test import TestCase
from django.shortcuts import reverse

class ProfileViewTestCase(TestCase):
    def setUp(self):
        pass


    def test_detail(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
