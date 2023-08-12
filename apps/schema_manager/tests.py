from django.utils.crypto import get_random_string
from django.urls import reverse
from apps.schema_manager.repositores import get_dynamic_table_model

from datalex.test_utils import ApiTestCase
from .models import DynamicTable


def valid_payload_factory() -> dict:
    payload = {
        "name": get_random_string(30),
        "fields": [
            {"name": get_random_string(30), "field_type": "number"},
            {"name": get_random_string(30), "field_type": "string"},
        ],
    }
    return payload


class TestDynamicTableCreate(ApiTestCase):
    def test_allowed_methods(self):
        payload = valid_payload_factory()
        for method in ("put", "get", "patch"):
            request_method = getattr(self.api_client, method)
            resp = request_method(reverse("table-create"), payload, format="json")
            self.assertEqual(resp.status_code, 405)

    def test_normal_post(self):
        self.assertEqual(DynamicTable.objects.count(), 0)
        payload = valid_payload_factory()
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(DynamicTable.objects.count(), 1)
        schema_row = DynamicTable.objects.first()
        self.assertEqual(schema_row.name, payload["name"])
        self.assertEqual(schema_row.fields, payload["fields"])

        payload["name"] = get_random_string(40)
        self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(DynamicTable.objects.count(), 2)

    def test_schema_exists(self):
        payload = valid_payload_factory()
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(DynamicTable.objects.count(), 1)
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(DynamicTable.objects.count(), 1)

    def test_bad_schema_name(self):
        payload = {
            "name": "bad schema name with spaces",
            "fields": [{"name": get_random_string(20), "field_type": "number"}],
        }
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_bad_field_name(self):
        payload = {
            "name": "schema_with_underscores",
            "fields": [
                {"name": get_random_string(20), "field_type": "number"},
                {"name": "bad field name with spaces", "field_type": "number"},
            ],
        }
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_bad_field_type(self):
        payload = {
            "name": "schema_with_underscores",
            "fields": [
                {"name": get_random_string(20), "field_type": "integer"},
            ],
        }
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_same_named_fields(self):
        payload = {
            "name": "new_schema",
            "fields": [
                {"name": "field1", "field_type": "number"},
                {"name": "field2", "field_type": "string"},
                {"name": "field1", "field_type": "boolean"},
            ],
        }
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 201)
        created_table = DynamicTable.objects.first()
        self.assertEqual(len(created_table.fields), 2)
        self.assertIn({"name": "field1", "field_type": "boolean"}, created_table.fields)
        self.assertIn({"name": "field2", "field_type": "string"}, created_table.fields)


class TestDynamicTableUpdate(ApiTestCase):
    def test_add_alter_delete(self):
        test_table_name = "master_table"
        payload = {
            "name": test_table_name,
            "fields": [
                {"name": "field1", "field_type": "number"},
                {"name": "field2", "field_type": "string"},
            ],
        }
        resp = self.api_client.post(reverse("table-create"), payload, format="json")
        self.assertEqual(resp.status_code, 201)

        del payload["name"]
        payload["fields"][0]["field_type"] = "boolean"
        payload["fields"].append({"name": "field3", "field_type": "number"})
        table_id = DynamicTable.objects.first().pk
        resp = self.api_client.put(reverse("table-update", kwargs={"pk": table_id}), payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(DynamicTable.objects.count(), 1)
        self.assertEqual(DynamicTable.objects.first().fields, payload["fields"])

        table_model = get_dynamic_table_model(test_table_name, payload["fields"])
        table_model.objects.create(field1=False, field2="ewqqwe", field3=321)
        self.assertEqual(table_model.objects.count(), 1)

        payload["fields"][0]["field_type"] = "number"
        self.api_client.put(reverse("table-update", kwargs={"pk": table_id}), payload, format="json")
        get_dynamic_table_model(test_table_name, payload["fields"])
        self.assertEqual(resp.status_code, 200)

        payload["fields"][1]["field_type"] = "number"
        resp = self.api_client.put(reverse("table-update", kwargs={"pk": table_id}), payload, format="json")
        get_dynamic_table_model(test_table_name, payload["fields"])
        # expect unable to convert string ("ewqqwe") to number type
        self.assertEqual(resp.status_code, 400)
        # check the rollback happened and we did not store any data
        payload["fields"][1]["field_type"] = "string"
        self.assertEqual(DynamicTable.objects.first().fields, payload["fields"])
