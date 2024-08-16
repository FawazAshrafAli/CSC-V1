from django.urls import path
from .views import (
    HomeView, 
    
    ServiceListView, RemoveServiceView, AddServiceView, 
    ServiceEnquiryListView, DeleteServiceEnquiryView,
    ServiceEnquiryDetailView, 
    
    ProductListView, RemoveProductView, AddProductView, 
    ProductEnquiryListView, DeleteProductEnquiryView, ProductEnquiryDetailView, 
    
    CscCenterListView, AddCscCenterView, DetailCscCenterView, 
    UpdateCscCenterView,

    AvailablePosterView, CreatePosterView,
    )

app_name = "users"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('services/', ServiceListView.as_view(), name="services"),
    path('remove_service/<str:slug>', RemoveServiceView.as_view(), name="remove_service"),
    path('add_services/', AddServiceView.as_view(), name="add_services"),
    path('service_enquiries/', ServiceEnquiryListView.as_view(), name="service_enquiries"),
    path('delete_service_enquiry/<str:slug>', DeleteServiceEnquiryView.as_view(), name="delete_service_enquiry"),
    path('service_enquiry/<str:slug>', ServiceEnquiryDetailView.as_view(), name="service_enquiry"),

    path('products/', ProductListView.as_view(), name="products"),
    path('remove_product/<str:slug>', RemoveProductView.as_view(), name="remove_product"),
    path('add_products/', AddProductView.as_view(), name="add_products"),
    path('product_enquiries/', ProductEnquiryListView.as_view(), name="product_enquiries"),
    path('delete_product_enquiry/<str:slug>', DeleteProductEnquiryView.as_view(), name="delete_product_enquiry"),
    path('product_enquiry/<str:slug>', ProductEnquiryDetailView.as_view(), name="product_enquiry"),

    path('available_posters/', AvailablePosterView.as_view(), name="available_posters"),
    path('create_poster/<str:slug>', CreatePosterView.as_view(), name="create_poster"),

    path('csc_centers/', CscCenterListView.as_view(), name="csc_centers"),
    path('add_csc/', AddCscCenterView.as_view(), name="add_csc"),
    path('csc_center/<str:slug>', DetailCscCenterView.as_view(), name="csc_center"),
    path('update_csc/<str:slug>', UpdateCscCenterView.as_view(), name="update_csc"),
]
