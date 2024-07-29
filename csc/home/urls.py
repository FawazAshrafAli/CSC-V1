from django.urls import path
from .views import (
    HomePageView, DetailCscView, SearchCscCenterView,
    ModifyListCscCenterView, FilterCscCenterListView
)

app_name = "home"

urlpatterns = [
    path('', HomePageView.as_view(), name="view"),    
    # path('filtered_location/', FilteredLocationView.as_view(), name="filtered_location"),
    # path('get_pincode_location/', PincodeLocationView.as_view(), name="get_pincode_location"),
    # path('locate_me/', LocateMeView.as_view(), name="locate_me"),

    path('csc_centers/', SearchCscCenterView.as_view(), name="csc_centers"),
    path('listing/', ModifyListCscCenterView.as_view(), name="listing"),
    path('filter_centers/', FilterCscCenterListView.as_view(), name="filter_centers"),

    path('csc/<pk>', DetailCscView.as_view(), name="csc"),
]
