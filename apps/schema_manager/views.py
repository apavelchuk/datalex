from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError

from .exceptions import DynamicTableRepositoryException
from .serializers import DynamicTableSerializer
from .repositores import dynamic_table_repo_factory
from .models import DynamicTable


class DynamicTableCreateView(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = DynamicTableSerializer
    queryset = DynamicTable.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError as exc:
            raise ValidationError(str(exc))
        dynamic_table_repo_factory().add(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DynamicTableUpdateView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = DynamicTableSerializer
    queryset = DynamicTable.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        try:
            dynamic_table_repo_factory().update(serializer.instance)
        except DynamicTableRepositoryException as exc:
            raise ValidationError(exc)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
