from django.urls import path
from .views import ListServiceView, DetailServiceView

app_name = "services"

urlpatterns = [
    path("", ListServiceView.as_view(), name="list"),
    path("detail/<pk>", DetailServiceView.as_view(), name="detail"),
]
