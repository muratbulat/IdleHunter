# API URL configuration
from django.urls import path
from .api import api_health, api_vm_list, api_vm_detail, api_data_sources

app_name = "api"
urlpatterns = [
    path("health/", api_health),
    path("vms/", api_vm_list),
    path("vms/<int:pk>/", api_vm_detail),
    path("data-sources/", api_data_sources),
]
