from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.db import models

from apps.schema_manager.repositores import dynamic_table_repo_factory
from .serializers import model_serializer_class_factory


class RowCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    def post(self, request, table_id: int):
        model = find_table_or_404(table_id)

        serializer = model_serializer_class_factory(model)(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RowListView(mixins.ListModelMixin, generics.GenericAPIView):
    def get(self, request, table_id: int):
        return self.list(request, table_id)

    def list(self, request, table_id: int):
        queryset = self.filter_queryset(self.get_queryset(table_id))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(queryset.model, page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset.model, queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self, table_id: int):
        model = find_table_or_404(table_id)
        return model.objects.all()

    def get_serializer(self, model, page, *args, **kwargs):
        serializer_class = self.get_serializer_class(model)
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(page, *args, **kwargs)

    def get_serializer_class(self, model: models.Model):
        return model_serializer_class_factory(model)


def find_table_or_404(table_id):
    try:
        return dynamic_table_repo_factory().get_by_id(table_id)
    except KeyError:
        raise NotFound(f"Cannot find table with ID '{table_id}'")
