from django.urls import path
from .views import (
    HomeView, 
    
    ServiceListView, RemoveServiceView, AddServiceView, 

    ServiceEnquiryListView, DeleteServiceEnquiryView,
    ServiceEnquiryDetailView, LeftoverServiceView,
    MarkServiceEnquiryAsViewedView,
    
    ProductListView, RemoveProductView, AddProductView,

    ProductEnquiryListView, DeleteProductEnquiryView, 
    ProductEnquiryDetailView, LeftoverProductView,
    MarkProductEnquiryAsViewedView,
    
    CscCenterListView, AddCscCenterView, DetailCscCenterView, 
    UpdateCscCenterView, SavePosterView, GetCurrentCscCenterView,
    GetCenterDataView,

    AvailablePosterView, CreatePosterView, MyPosterListView,
    DeleteMyPosterView, MyPosterDetailView, DownloadPosterView,

    MyProfileView, UpdateProfileView, ChangePasswordView,
    )

app_name = "users"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    path('services/', ServiceListView.as_view(), name="services"),
    path('remove_service/<str:slug>', RemoveServiceView.as_view(), name="remove_service"),
    path('add_services/<str:slug>', AddServiceView.as_view(), name="add_services"),
    path('leftover_services/<str:slug>', LeftoverServiceView.as_view(), name="leftover_services"),

    path('service_enquiries/', ServiceEnquiryListView.as_view(), name="service_enquiries"),
    path('delete_service_enquiry/<str:slug>', DeleteServiceEnquiryView.as_view(), name="delete_service_enquiry"),
    path('service_enquiry/<str:slug>', ServiceEnquiryDetailView.as_view(), name="service_enquiry"),
    path('viewed_service_enquiry/<str:slug>', MarkServiceEnquiryAsViewedView.as_view(), name="viewed_service_enquiry"),

    path('products/', ProductListView.as_view(), name="products"),
    path('remove_product/<str:slug>', RemoveProductView.as_view(), name="remove_product"),
    path('add_products/<str:slug>', AddProductView.as_view(), name="add_products"),
    path('leftover_products/<str:slug>', LeftoverProductView.as_view(), name="leftover_products"),

    path('product_enquiries/', ProductEnquiryListView.as_view(), name="product_enquiries"),
    path('delete_product_enquiry/<str:slug>', DeleteProductEnquiryView.as_view(), name="delete_product_enquiry"),
    path('product_enquiry/<str:slug>', ProductEnquiryDetailView.as_view(), name="product_enquiry"),
    path('viewed_product_enquiry/<str:slug>', MarkProductEnquiryAsViewedView.as_view(), name="viewed_product_enquiry"),

    path('available_posters/', AvailablePosterView.as_view(), name="available_posters"),
    path('my_posters/', MyPosterListView.as_view(), name="my_posters"),
    path('my_poster/<str:slug>', MyPosterDetailView.as_view(), name="my_poster"),
    path('create_poster/<str:slug>', CreatePosterView.as_view(), name="create_poster"),
    path('save_poster/', SavePosterView.as_view(), name="save_poster"),
    path('download_poster/<str:slug>', DownloadPosterView.as_view(), name="download_poster"),
    path('delete_poster/<str:slug>', DeleteMyPosterView.as_view(), name="delete_poster"),

    path('csc_centers/', CscCenterListView.as_view(), name="csc_centers"),
    path('add_csc/', AddCscCenterView.as_view(), name="add_csc"),
    path('csc_center/<str:slug>', DetailCscCenterView.as_view(), name="csc_center"),
    path('update_csc/<str:slug>', UpdateCscCenterView.as_view(), name="update_csc"),
    path('get_current_csc/', GetCurrentCscCenterView.as_view(), name="get_current_csc"),
    path('get_center_data/', GetCenterDataView.as_view(), name="get_center_data"),

    path('my_profile/', MyProfileView.as_view(), name = 'my_profile'),
    path('update_profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
]
