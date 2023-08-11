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
    return fields


def validate_table_name(new_name: str):
    if not re.match(r'^\w+$', new_name):
        raise serializers.ValidationError("Please use only alphanumeric and underscore symbols for table name.")
    return new_name


class DynamicTableSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[validate_table_name])
    fields = serializers.ListField(child=serializers.DictField(), validators=[validate_fields])

    class Meta:
        model = DynamicTable
        fields = ["id", "name", "fields"]
