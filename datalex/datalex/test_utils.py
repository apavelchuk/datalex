from rest_framework.test import APIClient
from django.test import TestCase
from django.db import connections


class ApiTestCase(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        return super().setUp()
