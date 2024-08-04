from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages

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

