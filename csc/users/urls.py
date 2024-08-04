from django.urls import path
from .views import (HomeView, ServiceListView, RemoveServiceView, 
                    AddServiceView)

app_name = "users"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('services/', ServiceListView.as_view(), name="services"),
    path('remove_service/<str:slug>', RemoveServiceView.as_view(), name="remove_service"),
    path('add_service/', AddServiceView.as_view(), name="add_service"),
]
