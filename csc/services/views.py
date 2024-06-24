from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, DetailView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .models import Service

@method_decorator(never_cache, name="dispatch")
class ListServiceView(ListView):
    model = Service
    queryset = Service.objects.all()
    template_name = 'services/list.html'
    context_object_name = "services"


@method_decorator(never_cache, name="dispatch")
class DetailServiceView(DetailView):
    model = Service
    template_name = 'services/detail.html'
    context_object_name = "service"

