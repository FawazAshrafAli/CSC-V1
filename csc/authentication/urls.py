from django.urls import path
from .views import AuthenticationView, LogoutView

app_name = "authentication"

urlpatterns = [
    path('', AuthenticationView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
]
