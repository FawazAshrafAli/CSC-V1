from django.urls import path
from .views import HomePageView, PincodeLocationView, LocateMeView, FilteredLocationView, DetailCscView

app_name = "home"

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),    
    path('filtered_location/', FilteredLocationView.as_view(), name="filtered_location"),
    path('get_pincode_location/', PincodeLocationView.as_view(), name="get_pincode_location"),
    path('locate_me/', LocateMeView.as_view(), name="locate_me"),

    path('csc/<pk>', DetailCscView.as_view(), name="csc"),
]
