from django.urls import path
from apps.schema_manager import views


urlpatterns = [
    path('api/table', views.DynamicTableCreateView.as_view(), name="table-create"),
    path('api/table/<int:pk>', views.DynamicTableUpdateView.as_view(), name="table-update"),
]
