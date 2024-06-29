from django.shortcuts import render
from django.views.generic import TemplateView

class ContactUsView(TemplateView):
    template_name = "contact_us/contact_us.html"
