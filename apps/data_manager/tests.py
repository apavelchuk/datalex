from django.urls import reverse

from datalex.test_utils import ApiTestCase, dynamic_table_factory


def schema_factory() -> dict:
    payload = {
        "name": "main_schema",
        "fields": [
            {"name": "fnumber", "field_type": "number"},
            {"name": "fstring", "field_type": "string"},
            {"name": "fbool", "field_type": "boolean"},
        ],
    }
    return payload


class TestRowCreate(ApiTestCase):
    def test_no_schema_with_this_id(self):
        resp = self.api_client.post(reverse("row-create", kwargs={"table_id": 132}), format="json")
        self.assertEqual(resp.status_code, 404)

    def test_successful_create(self):
        schema = schema_factory()
        table_id, table = dynamic_table_factory(schema["name"], schema["fields"])
        self.assertEqual(table.objects.count(), 0)
        payload = {"fnumber": 32141, "fstring": "some random String VALUE", "fbool": False}
        resp = self.api_client.post(reverse("row-create", kwargs={"table_id": table_id}), payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(table.objects.count(), 1)
        created_obj = table.objects.first()
        self.assertEqual(created_obj.fnumber, payload["fnumber"])
        self.assertEqual(created_obj.fstring, payload["fstring"])
        self.assertEqual(created_obj.fbool, payload["fbool"])

    def test_all_fields_required(self):
        schema = schema_factory()
        table_id, table = dynamic_table_factory(schema["name"], schema["fields"])
        self.assertEqual(table.objects.count(), 0)
        payload = {"fnumber": 32141}
        resp = self.api_client.post(reverse("row-create", kwargs={"table_id": table_id}), payload, format="json")
        self.assertEqual(resp.status_code, 400)
        payload = {"fnumber": 32141, "fbool": True}
        resp = self.api_client.post(reverse("row-create", kwargs={"table_id": table_id}), payload, format="json")
        self.assertEqual(resp.status_code, 400)


class TestRowList(ApiTestCase):
    def test_no_schema_with_this_id(self):
        resp = self.api_client.get(reverse("row-list", kwargs={"table_id": 132}), format="json")
        self.assertEqual(resp.status_code, 404)

    def test_successful_list(self):
        schema = schema_factory()
        table1_id, _ = dynamic_table_factory(f"{schema['name']}_1", schema["fields"])
        table2_id, _ = dynamic_table_factory(f"{schema['name']}_2", schema["fields"])

        payload1 = {"fnumber": 32141, "fstring": "some random String VALUE", "fbool": False}
        self.api_client.post(reverse("row-create", kwargs={"table_id": table1_id}), payload1, format="json")
        payload2 = {"fnumber": 79482, "fstring": "second row value", "fbool": True}
        self.api_client.post(reverse("row-create", kwargs={"table_id": table1_id}), payload2, format="json")

        resp = self.api_client.get(reverse("row-list", kwargs={"table_id": table1_id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

        resp = self.api_client.get(reverse("row-list", kwargs={"table_id": table2_id}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

        resp = self.api_client.get(reverse("row-list", kwargs={"table_id": table1_id}) + "?limit=1&offset=1")
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        self.assertEqual(len(resp.data["results"]), 1)
