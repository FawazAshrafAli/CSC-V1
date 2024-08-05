from django.urls import path
from .views import (HomeView, ServiceListView, RemoveServiceView, 
                    AddServiceView, ServiceEnquiryListView, DeleteServiceEnquiryView,
                    ServiceEnquiryDetailView, ProductListView, RemoveProductView,
                    AddProductView)

app_name = "users"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('services/', ServiceListView.as_view(), name="services"),
    path('remove_service/<str:slug>', RemoveServiceView.as_view(), name="remove_service"),
    path('add_services/', AddServiceView.as_view(), name="add_services"),
    path('enquiries/', ServiceEnquiryListView.as_view(), name="enquiries"),
    path('delete_enquiry/<str:slug>', DeleteServiceEnquiryView.as_view(), name="delete_enquiry"),
    path('enquiry/<str:slug>', ServiceEnquiryDetailView.as_view(), name="enquiry"),

    path('products/', ProductListView.as_view(), name="products"),
    path('remove_product/<str:slug>', RemoveProductView.as_view(), name="remove_product"),
    path('add_products/', AddProductView.as_view(), name="add_products"),
]
