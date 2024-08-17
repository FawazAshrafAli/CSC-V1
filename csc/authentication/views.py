from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.http import Http404
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .tasks import send_otp_email
from .models import User, UserOtp

class AuthenticationView(View):
    template_name = 'authentication/login.html'
    success_url = reverse_lazy('csc_admin:home')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect(self.success_url)
            else:
                return redirect(reverse_lazy('users:home'))
        
        username = request.GET.get('username')
        password = request.GET.get('password')

        if username and password:
            user = authenticate(request, username = username, password = password)
            if user is not None:
                login(request, user)
                return redirect(self.success_url)
            else:
                messages.error(request, 'Invalid username or password.')
                
        return render(request, self.template_name)


class LogoutView(View):
    success_url = reverse_lazy('home:view')
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return redirect(self.success_url)
        else:
            return redirect(reverse_lazy('authentication:login'))

class ResetPasswordWithOtpView(UpdateView):
    model = User
    fields = ['password']
    template_name = 'authentication/forgot_password.html'
    success_url = reverse_lazy('authentication:login')
    pk_url_kwarg = 'email'
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(self.model, email = self.kwargs.get('email'))
        except Http404:
            pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.kwargs.get('email')
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:            
            user_otp = get_object_or_404(UserOtp, user = self.object)
        except Http404:
            messages.error(request, 'No otp has been generated for your account')
            return redirect(self.redirect_url)

        otp = request.POST.get('otp')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')

        if user_otp.otp != otp:
            messages.error(request, "Invalid OTP")
            return redirect(self.redirect_url)

        if timezone.now() > user_otp.updated + timedelta(minutes=5):
            messages.error(request, "Expired OTP.")
            return redirect(self.redirect_url)
        
        if password != repeat_password:
            messages.error(request, "Password not matching.")
            return redirect(self.redirect_url)
        
        self.object.set_password(password)
        self.object.save()

        user_otp.delete()
        messages.success(request, "Successfully resetted password")
        return redirect(self.get_success_url())
        



class ForgotPasswordView(View):
    redirect_url = reverse_lazy('authentication:login')
    success_url = reverse_lazy('authentication:reset_password_with_otp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email = self.request.POST.get('email')
        context['email'] = email
        return context
    

    def post(self, request, *args, **kwargs):
        try:
            email = request.POST.get('email')
            user = None

            try:
                user = get_object_or_404(User, email = email)
            except Http404:
                pass

            if not email:
                messages.warning(request, "Please provide your email id.")
                return redirect(self.redirect_url)

            if not User.objects.filter(email = email).exists():
                messages.error(request, "Invalid Email Id")
                return redirect(self.redirect_url)

            otp = get_random_string(length=6, allowed_chars='1234567890')

            UserOtp.objects.update_or_create(user = user, defaults={'otp': otp})

            # send_otp_email.delay(email, otp)

            subject = 'OTP for setting password'
            message = f'Your OTP code is {otp}. It is valid for the next 5 minutes.'
            from_email = 'w3digitalpmna@gmail.com'
            receipient_list = [email]

            try:
                send_mail(subject, message, from_email, receipient_list)
            except Exception as e:
                print(e)
                pass

            messages.success(request, "OTP has been sent to your email.")
            return redirect(reverse('authentication:reset_password_with_otp', kwargs={'email': email}))

        except Exception as e:
            print(e)
            return redirect(self.redirect_url)