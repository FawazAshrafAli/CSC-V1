from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .models import Service

class BaseServiceView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        context['service_page'] = True
        return context

@method_decorator(never_cache, name="dispatch")
class ListServiceView(BaseServiceView, ListView):
    model = Service
    queryset = Service.objects.all()
    template_name = 'services/list.html'
    context_object_name = "services"


@method_decorator(never_cache, name="dispatch")
class DetailServiceView(BaseServiceView, DetailView):
    model = Service
    template_name = 'services/detail.html'
    context_object_name = "service"
    slug_url_kwarg = 'slug'

