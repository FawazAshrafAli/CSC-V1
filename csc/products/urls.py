from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryFilteredProductsListView

app_name = "products"

urlpatterns = [
    path('', ProductListView.as_view(), name="products"),
    path('product/<str:slug>', ProductDetailView.as_view(), name="product"),
    path('tags/<str:slug>', CategoryFilteredProductsListView.as_view(), name="category"),
]
