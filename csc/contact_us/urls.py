from django.urls import path
from .views import ContactUsView

app_name = "contact_us"

urlpatterns = [
    path('', ContactUsView.as_view(), name = "view")
]
