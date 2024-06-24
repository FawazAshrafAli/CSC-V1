from django.urls import path
from .views import (
    AdminHomeView, ListServiceView, DetailServiceView, 
    UpdateServiceView, CreateServiceView, JsonSeviceDetailView, 
    DeleteServiceView
    )

app_name = "csc_admin"

urlpatterns = [
    path("", AdminHomeView.as_view(), name="home"),

    path("services/", ListServiceView.as_view(), name="services"),
    path("service/<pk>", DetailServiceView.as_view(), name="service"),
    path("create_service/", CreateServiceView.as_view(), name="create_service"),
    path("update_service/<pk>", UpdateServiceView.as_view(), name="update_service"),
    path("delete_service/<pk>", DeleteServiceView.as_view(), name="delete_service"),

    path("get_service_details/<pk>", JsonSeviceDetailView.as_view(), name="get_service_details"),
]
