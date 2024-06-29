from django.shortcuts import render
from django.views.generic import TemplateView

class AboutUsView(TemplateView):
    template_name = 'about_us/about_us.html'
