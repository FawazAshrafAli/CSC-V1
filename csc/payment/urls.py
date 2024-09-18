from django.urls import path
from .views import PaymentView, PaymentSuccessView

app_name = "payment"

urlpatterns = [
    path("<str:slug>", PaymentView.as_view(), name="payment"),
    path("success/", PaymentSuccessView.as_view(), name="success"),
]
