from typing import List, Tuple
from django.db import models
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.schema_manager.models import DynamicTable
from apps.schema_manager.repositores import get_dynamic_table_model


class ApiTestCase(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        return super().setUp()


def dynamic_table_factory(name: str, fields: List[dict]) -> Tuple[int, models.Model]:
    resp = APIClient().post(reverse("table-create"), {"name": name, "fields": fields}, format="json")
    dynamic_table = get_dynamic_table_model(resp.data["name"], resp.data["fields"])
    return DynamicTable.objects.get(name=name).pk, dynamic_table
