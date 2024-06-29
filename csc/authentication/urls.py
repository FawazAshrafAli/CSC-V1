from django.urls import path
from .views import AuthenticationView

app_name = "authentication"

urlpatterns = [
    path('', AuthenticationView.as_view(), name = 'login'),
]
