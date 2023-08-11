from typing import List
from django.db import models
from pydantic import BaseModel
from enum import Enum

NAME_MAX_LENGTH = 255


class FieldType(str, Enum):
    string = "string"
    number = "number"
    boolean = "boolean"


class Field(BaseModel):
    name: str
    field_type: FieldType


class DynamicTable(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    fields: List[Field] = models.JSONField()
