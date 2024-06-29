from django.shortcuts import render
from django.views.generic import TemplateView

class AuthenticationView(TemplateView):
    template_name = 'authentication/login.html'
