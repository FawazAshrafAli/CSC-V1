from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib import messages

from services.models import Service, ServiceEnquiry
from csc_center.models import CscCenter

class BaseUserView(LoginRequiredMixin, View):
    login_url = reverse_lazy('authentication:login')
    model = CscCenter

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(self.model, email = self.request.user.email)
        except Http404:
            return redirect(reverse_lazy('authentication:logout'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        context['center'] = self.object    

        excluding_services = self.object.services.all()
        context['services_left'] = Service.objects.all().exclude(id__in=excluding_services.values_list('id', flat=True))

        return context
    

class HomeView(BaseUserView, TemplateView):
    template_name = 'user_home/home.html'


class ServiceListView(BaseUserView, ListView):
    template_name = 'user_services/list.html'
    context_object_name = 'services'

    def get_context_data(self):
        context = super().get_context_data()
        context['service_page'] = True
        return context

    def get_queryset(self):
        center = super().get_object()   
        services = center.services.all()
        return services
    

class RemoveServiceView(BaseUserView, View):
    success_url = reverse_lazy('users:services')
    redirect_url = success_url

    def get(self, request, *args, **kwargs):
        center = super().get_object()

        try:
            service_id = get_object_or_404(Service, slug = kwargs['slug']).pk
        except Http404:
            messages.error(self.request, 'Service not found')
            return redirect(self.redirect_url)
        
        center.services.remove(service_id)
        center.save()
        messages.success(self.request, 'Service removed successfully')
        return redirect(self.success_url)
    

class AddServiceView(BaseUserView, View):
    success_url = reverse_lazy('users:services')
    redirect_url = success_url

    def post(self, request, *args, **kwargs):
        center = super().get_object()

        services = request.POST.getlist('services')

        for service in services:
            center.services.add(service)
            center.save()
        
        messages.success(request, 'Added Services')
        return redirect(self.success_url)


