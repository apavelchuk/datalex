from typing import Dict, List, Tuple, Set
from abc import ABC, abstractmethod
from functools import lru_cache
from django.db import connection, models
from django.db.utils import DataError

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
        self.tables: Dict[int, models.Model] = self.init_repo()

    def init_repo(self) -> Dict[int, models.Model]:
        tables: Dict[int, models.Model] = {}
        existing_schemas = DynamicTable.objects.all().order_by("pk")
        for schema in existing_schemas:
            tables[schema.pk] = get_dynamic_table_model(schema.name, schema.fields)
        return tables

    def add(self, new_schema_model: DynamicTable) -> models.Model:
        new_dynamic_table = get_dynamic_table_model(new_schema_model.name, new_schema_model.fields)

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(new_dynamic_table)
        self.tables[new_schema_model.pk] = new_dynamic_table
        return new_dynamic_table

    def update(self, updated_schema_model: DynamicTable) -> models.Model:
        old_dynamic_table = self.get_by_id(updated_schema_model.pk)
        to_create, to_alter, to_delete = compare_existing_table_to_new_schema(old_dynamic_table, updated_schema_model)

        with connection.schema_editor() as schema_editor:
            for field_to_add in to_create:
                schema_editor.add_field(old_dynamic_table, field_to_add)
            for field_to_delete in to_delete:
                schema_editor.remove_field(old_dynamic_table, field_to_delete)
            for old_field, new_field in to_alter:
                try:
                    schema_editor.alter_field(old_dynamic_table, old_field, new_field)
                except DataError as exc:
                    raise DynamicTableRepositoryException(str(exc))
        self.refresh_from_db(updated_schema_model.pk)
        return old_dynamic_table

    def get_by_id(self, table_id: int) -> models.Model:
        return self.tables[table_id]

    def refresh_from_db(self, table_id: int) -> models.Model:
        table_from_db = DynamicTable.objects.get(pk=table_id)
        self.tables[table_id] = get_dynamic_table_model(table_from_db.name, table_from_db.fields)
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


def compare_existing_table_to_new_schema(
    old_dynamic_table: models.Model,
    updated_schema_model: DynamicTable,
) -> Tuple[List[models.Field], List[Tuple[models.Field, models.Field]], List[models.Field]]:
    existing_fields = {f.column: f for f in old_dynamic_table._meta.get_fields(include_parents=False) if f.column != "id"}
    processed_fields: Set[str] = set()
    to_create, to_alter, to_delete = {}, {}, []
    for field in updated_schema_model.fields:
        typed_field = Field(**field)
        if typed_field.name not in existing_fields:
            model_field = get_model_field_for_field_type(typed_field.field_type)
            model_field.column, model_field.name, model_field.verbose_name = typed_field.name, typed_field.name, typed_field.name
            to_create[typed_field.name] = model_field
        else:
            old_field = existing_fields[typed_field.name]
            new_field = get_model_field_for_field_type(typed_field.field_type)
            if type(old_field) != type(new_field):
                new_field.column, new_field.name, new_field.verbose_name = old_field.column, old_field.column, old_field.column
                to_alter[typed_field.name] = (old_field, new_field)
            processed_fields.add(typed_field.name)
    unprocessed_field_names = set(existing_fields.keys()) - processed_fields
    for unprocessed_field_name in unprocessed_field_names:
        to_delete.append(existing_fields[unprocessed_field_name])

    return list(to_create.values()), list(to_alter.values()), to_delete


@lru_cache
def dynamic_table_repo_factory() -> DynamicTableRepositoryInterface:
    return DynamicTableRepository()
