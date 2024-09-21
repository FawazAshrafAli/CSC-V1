from django.urls import path
from .views import (
    Error404,
    HomePageView, SearchCscCenterView,
    FilterAndSortCscCenterView, CscCenterDetailView,
    NearMeCscCenterView, ServiceRequestView, ProductRequestView, getStates
)

app_name = "home"

urlpatterns = [
    path('', HomePageView.as_view(), name="view"),    

    path('error404/', Error404.as_view(), name="error404"),

    path('service_request/<str:slug>', ServiceRequestView.as_view(), name="service_request"),
    path('product_request/<str:slug>', ProductRequestView.as_view(), name="product_request"),
    path('centers_near_me/<latitude>/<longitude>', NearMeCscCenterView.as_view(), name="centers_near_me"),

    path('csc_centers/', SearchCscCenterView.as_view(), name="csc_centers"),
    path('filter_and_sort_centers/', FilterAndSortCscCenterView.as_view(), name="filter_and_sort_csc"),


    path('csc_center/<slug>', CscCenterDetailView.as_view(), name="csc_center"),

    path('states/', getStates, name="states"),
]
