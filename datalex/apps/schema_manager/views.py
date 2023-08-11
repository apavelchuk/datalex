from rest_framework import generics, mixins, status
from rest_framework.response import Response
from django.db import transaction

from .serializers import DynamicTableSerializer
from .repositores import dynamic_table_repo_factory
from .models import DynamicTable


class DynamicTableView(mixins.CreateModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = DynamicTableSerializer
    queryset = DynamicTable.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        dynamic_table_repo_factory().add(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def put(self, request, *args, **kwargs):
        updated_table = self.update(request, *args, **kwargs)
        dynamic_table_repo_factory().update(updated_table)
        return updated_table
