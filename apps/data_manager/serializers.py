from django.db import models
from rest_framework.serializers import ModelSerializer


def model_serializer_class_factory(model: models.Model):
    serializer_class = type(model._meta.model_name, (ModelSerializer,), {})
    fields_list = [f.name for f in model._meta.get_fields()]
    extra_kwargs = {fname: {"required": True} for fname in fields_list if fname != "id"}
    serializer_class.Meta = type("Meta", (), {"model": model, "fields": fields_list, "extra_kwargs": extra_kwargs})  # type: ignore[attr-defined]
    return serializer_class
