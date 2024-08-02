from django.urls import path
from .views import (
    HomePageView, SearchCscCenterView,
    FilterAndSortCscCenterView, CscCenterDetailView,
    NearMeCscCenterView,
)

app_name = "home"

urlpatterns = [
    path('', HomePageView.as_view(), name="view"),    
    # path('filtered_location/', FilteredLocationView.as_view(), name="filtered_location"),
    # path('get_pincode_location/', PincodeLocationView.as_view(), name="get_pincode_location"),
    path('centers_near_me/<latitude>/<longitude>', NearMeCscCenterView.as_view(), name="centers_near_me"),

    path('csc_centers/', SearchCscCenterView.as_view(), name="csc_centers"),
    path('filter_and_sort_centers/', FilterAndSortCscCenterView.as_view(), name="filter_and_sort_csc"),

    # path('csc/<pk>', DetailCscView.as_view(), name="csc"),

    path('csc_center/<slug>', CscCenterDetailView.as_view(), name="csc_center"),
]
