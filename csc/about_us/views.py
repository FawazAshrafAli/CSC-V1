from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView

from services.models import Service

class AboutUsView(TemplateView):
    template_name = 'about_us/about_us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        context['about_us_page'] = True
        return context
