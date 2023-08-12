import re

from typing import List
from django.db import models
from pydantic import BaseModel, validator
from enum import Enum

NAME_MAX_LENGTH = 255


class FieldType(str, Enum):
    string = "string"
    number = "number"
    boolean = "boolean"


class Field(BaseModel):
    name: str
    field_type: FieldType

    @validator("name")
    def validate_name(cls, value):
        if not re.match(r"^\w+$", value):
            raise ValueError("my_field must contain only [A-Za-z_0-9] symbols.")
        return value


class DynamicTable(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    fields = models.JSONField()
