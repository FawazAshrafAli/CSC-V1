from django.urls import path
from .views import AuthenticationView, LogoutView, ForgotPasswordView, ResetPasswordWithOtpView

app_name = "authentication"

urlpatterns = [
    path('', AuthenticationView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('reset_password_with_otp/<str:email>', ResetPasswordWithOtpView.as_view(), name = 'reset_password_with_otp'),
    path('forgot_password/', ForgotPasswordView.as_view(), name = 'forgot_password'),
]
