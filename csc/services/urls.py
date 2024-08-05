from django.urls import path
from .views import ListServiceView, DetailServiceView

app_name = "services"

urlpatterns = [
    path("", ListServiceView.as_view(), name="services"),
    path("service/<str:slug>", DetailServiceView.as_view(), name="service"),
]
