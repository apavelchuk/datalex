from django.urls import path
from apps.schema_manager import views


urlpatterns = [
    path('api/table', views.DynamicTableView.as_view(), name="table-upsert"),
]
