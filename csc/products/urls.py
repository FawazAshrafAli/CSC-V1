from django.urls import path
from .views import ProductsView

app_name = "products"

urlpatterns = [
    path('', ProductsView.as_view(), name="view"),
]
