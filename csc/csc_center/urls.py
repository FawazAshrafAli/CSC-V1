from django.urls import path
from .views import CreateCscCenterView

app_name = "csc_center"

urlpatterns = [
    path('', CreateCscCenterView.as_view(), name="create"),
]
