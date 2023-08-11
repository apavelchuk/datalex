from django.urls import path
from apps.schema_manager import views as schema_views
from apps.data_manager import views as data_views


urlpatterns = [
    path('api/table/<int:table_id>/rows', data_views.RowListView.as_view(), name="row-list"),
    path('api/table/<int:table_id>/row', data_views.RowCreateView.as_view(), name="row-create"),
    path('api/table/<int:pk>', schema_views.DynamicTableUpdateView.as_view(), name="table-update"),
    path('api/table', schema_views.DynamicTableCreateView.as_view(), name="table-create"),
]
