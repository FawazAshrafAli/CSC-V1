from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib import messages

from products.models import Product
from services.models import Service, ServiceEnquiry
from csc_center.models import CscCenter

class BaseUserView(LoginRequiredMixin, View):
    login_url = reverse_lazy('authentication:login')
    model = CscCenter

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(CscCenter, email = self.request.user.email)
        except Http404:
            return redirect(reverse_lazy('authentication:logout'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        try:
            self.object = self.get_object()
            context['center'] = self.object    

            excluding_services = self.object.services.all()
            context['services_left'] = Service.objects.all().exclude(id__in=excluding_services.values_list('id', flat=True))

            excluding_products = self.object.products.all()
            context['products_left'] = Product.objects.all().exclude(id__in=excluding_products.values_list('id', flat=True))
        except Exception as e:
            print(e)
            pass

        return context
    

class HomeView(BaseUserView, TemplateView):
    template_name = 'user_home/home.html'


# Service
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context

    def post(self, request, *args, **kwargs):
        center = super().get_object()

        services = request.POST.getlist('services')

        for service in services:
            center.services.add(service)
            center.save()
        
        messages.success(request, 'Added Services')
        return redirect(self.success_url)


class ServiceEnquiryListView(BaseUserView, ListView):
    model = ServiceEnquiry
    template_name = 'user_services/enquiry_list.html'
    context_object_name = 'enquiries'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context

    def get_queryset(self):
        return ServiceEnquiry.objects.filter(csc_center__email = self.request.user.email).order_by('-created')
    

class ServiceEnquiryDetailView(BaseUserView, DetailView):
    model = ServiceEnquiry
    template_name = 'user_services/enquiry_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'enquiry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context
    
    def get_object(self, **kwargs):
        try:
            self.object = get_object_or_404(ServiceEnquiry, slug = self.kwargs['slug'])
            print(self.object)
            return self.object
        except Http404:
            return redirect(reverse_lazy('users:enquiries'))
    

class DeleteServiceEnquiryView(BaseUserView, View):
    model = ServiceEnquiry
    success_url = reverse_lazy('users:enquiries')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(ServiceEnquiry, slug = self.kwargs['slug'])
        except Http404:
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Enquiry deleted successfully')
        return redirect(self.success_url)


# Products

class ProductListView(BaseUserView,ListView):
    template_name = 'user_products/list.html'
    context_object_name = 'products'

    def get_queryset(self):
        center = super().get_object()   
        products = center.products.all()
        return products
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_page'] = True
        return context    
    


class RemoveProductView(BaseUserView, View):
    success_url = reverse_lazy('users:products')
    redirect_url = success_url

    def get(self, request, *args, **kwargs):
        center = super().get_object()

        try:
            product_id = get_object_or_404(Product, slug = kwargs['slug']).pk
        except Http404:
            messages.error(self.request, 'Product not found')
            return redirect(self.redirect_url)
        
        center.products.remove(product_id)
        center.save()
        messages.success(self.request, 'Product removed successfully')
        return redirect(self.success_url)
    

class AddProductView(BaseUserView, View):
    success_url = reverse_lazy('users:products')
    redirect_url = success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_page'] = True
        return context

    def post(self, request, *args, **kwargs):
        center = super().get_object()

        products = request.POST.getlist('products')

        for product in products:
            center.products.add(product)
            center.save()
        
        messages.success(request, 'Added Products')
        return redirect(self.success_url)