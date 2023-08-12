import re

from typing import List
from pydantic import ValidationError
from rest_framework import serializers
from .models import DynamicTable, Field


def validate_fields(fields: List[dict]):
    try:
        [Field(**f) for f in fields]
    except ValidationError as exc:
        raise serializers.ValidationError(str(exc))


def validate_table_name(new_name: str):
    if not re.match(r"^\w+$", new_name):
        raise serializers.ValidationError("Please use only alphanumeric and underscore symbols for table name.")


class DynamicTableCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[validate_table_name])
    fields = serializers.ListField(child=serializers.DictField(), validators=[validate_fields])

    class Meta:
        model = DynamicTable
        fields = ["id", "name", "fields"]

    def to_internal_value(self, data):
        if data.get("fields"):
            data["fields"] = merge_same_named_fields(data["fields"])
        return super().to_internal_value(data)


class DynamicTableUpdateSerializer(serializers.ModelSerializer):
    fields = serializers.ListField(child=serializers.DictField(), validators=[validate_fields])

    class Meta:
        model = DynamicTable
        fields = ["fields"]

    def to_internal_value(self, data):
        if data.get("fields"):
            data["fields"] = merge_same_named_fields(data["fields"])
        return super().to_internal_value(data)


def merge_same_named_fields(fields: list):
    fields_without_dupes = {f["name"]: f for f in fields}
    return list(fields_without_dupes.values())
