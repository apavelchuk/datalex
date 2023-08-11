from typing import Dict, List
from abc import ABC, abstractmethod
from functools import lru_cache
from django.db import connection, models

from .models import DynamicTable, Field, FieldType
from .exceptions import DynamicTableRepositoryException


CHARFIELD_MAX_LENGHT = 255
USER_TABLES_PREFIX = "user_tables_"


class DynamicTableRepositoryInterface(ABC):
    @abstractmethod
    def add(self, new_schema_model: DynamicTable) -> models.Model:
        raise NotImplementedError()

    @abstractmethod
    def update(self, new_schema_model: DynamicTable) -> models.Model:
        raise NotImplementedError()


class DynamicTableRepository(DynamicTableRepositoryInterface):
    def __init__(self):
        tables_from_db = DynamicTable.objects.all().order_by("pk")
        self.tables: Dict[int, DynamicTable] = {t.pk: t for t in tables_from_db}

    def add(self, new_schema_model: DynamicTable) -> models.Model:
        new_dynamic_table = get_dynamic_table_model(new_schema_model.name, new_schema_model.fields)
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(new_dynamic_table)
        self.tables[new_schema_model.pk] = new_schema_model
        return new_dynamic_table

    def update(self) -> DynamicTable:
        pass

    def get_by_id(self, table_id: int) -> DynamicTable:
        return self.tables[table_id]


def get_dynamic_table_model(model_name: str, fields: List[dict]) -> models.Model:
    typed_fields = [Field(**f) for f in fields]
    model_fields = get_model_fields_from_typed_fields(typed_fields)
    model = type(model_name, (models.Model,), model_fields)
    model._meta.db_table = get_model_db_table_name(model)
    return model


def get_model_fields_from_typed_fields(typed_fields: List[Field]) -> Dict[str, models.Field]:
    db_fields = {"__module__": __name__}
    for field in typed_fields:
        db_fields[field.name] = get_model_field_for_field_type(field.field_type)
    return db_fields


def get_model_field_for_field_type(field_type: FieldType) -> models.Field:
    match field_type:
        case FieldType.string:
            return models.CharField(max_length=CHARFIELD_MAX_LENGHT, null=True, blank=True)
        case FieldType.number:
            return models.IntegerField(null=True, blank=True)
        case FieldType.boolean:
            return models.BooleanField(null=True, blank=True)
        case _:
            raise DynamicTableRepositoryException(f"Field type '{field_type}' is not supported.")


def get_model_db_table_name(model: models.Model) -> str:
    return USER_TABLES_PREFIX + model._meta.db_table.replace(model._meta.app_label, "")


@lru_cache
def dynamic_table_repo_factory() -> DynamicTableRepositoryInterface:
    return DynamicTableRepository()
