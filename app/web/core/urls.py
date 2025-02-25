from django.urls import path
from .views import export_excel, DataView

urlpatterns = [
    path("", DataView.as_view(), name="data"),
    path("export-excel/", export_excel, name="export_excel"),
]
