from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse

from products.models import Product, ProductEnquiry
from services.models import Service, ServiceEnquiry
from csc_center.models import (CscCenter, SocialMediaLink, State,
                                District, Block, CscKeyword, 
                                CscNameType)

class BaseUserView(LoginRequiredMixin, View):
    login_url = reverse_lazy('authentication:login')

    def get_context_data(self, **kwargs):
        context = {}
        try:
            centers = CscCenter.objects.filter(email = self.request.user.email)
            context['centers'] = centers
            context['center'] = centers[0]

        except Exception as e:
            print(e)
            pass

        return context
    

class HomeView(BaseUserView, TemplateView):
    template_name = 'user_home/home.html'


# Service
class BaseServiceView(BaseUserView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context
    

class ServiceListView(BaseServiceView, ListView):
    template_name = 'user_services/list.html'

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            center_slug = request.GET.get('center_slug')
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)
                services = center.services.all()
                services_list = []
                for count, service in enumerate(services):
                    services_list.append({'name': service.name, 'image': service.image.url if service.image else None, 'slug': service.slug, 'count': count+1})
                return JsonResponse({'services': services_list})
            except Http404:
                pass
        return super().get(request, *args, **kwargs)
            
    

class RemoveServiceView(BaseServiceView, View):
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
    

class AddServiceView(BaseServiceView, View):
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


class ServiceEnquiryListView(BaseServiceView, ListView):
    model = ServiceEnquiry
    template_name = 'user_services/enquiry_list.html'
    context_object_name = 'enquiries'

    def get_queryset(self):
        center = CscCenter.objects.filter(email = self.request.user.email).first()
        enquiries = self.model.objects.filter(csc_center = center).order_by('-created')
        return enquiries
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enquiries'] = self.get_queryset()
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            center_slug = request.GET.get('center_slug')
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)
                enquiries = self.model.objects.filter(csc_center = center)
                enquiries_list = []
                for count, enquiry in enumerate(enquiries):
                    enquiries_list.append({'applicant_name': enquiry.applicant_name, 'applicant_email': enquiry.applicant_email, 'applicant_phone': enquiry.applicant_phone, 'get_absolute_url': enquiry.get_absolute_url, 'service': enquiry.service.name, 'count': count+1})
                return JsonResponse({'enquiries': enquiries_list})
            except Http404:
                pass
        return super().get(request, *args, **kwargs)
    

class ServiceEnquiryDetailView(BaseServiceView, DetailView):
    model = ServiceEnquiry
    template_name = 'user_services/enquiry_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'enquiry'
    
    def get_object(self, **kwargs):
        try:
            self.object = get_object_or_404(ServiceEnquiry, slug = self.kwargs['slug'])
            return self.object
        except Http404:
            return redirect(reverse_lazy('users:enquiries'))
    

class DeleteServiceEnquiryView(BaseServiceView, View):
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
class ProductBaseView(BaseUserView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_page'] = True
        return context  
    
    
class ProductListView(ProductBaseView,ListView):
    template_name = 'user_products/list.html'
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            center_slug = request.GET.get('center_slug')
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)
                products = center.products.all()
                product_list = []
                for count, product in enumerate(products):
                    product_list.append({'name': product.name, 'image': product.image.url if product.image else None, 'slug': product.slug, 'count': count+1, 'price': product.price})
                return JsonResponse({'products': product_list})
            except Http404:
                pass
        return super().get(request, *args, **kwargs)
    

class RemoveProductView(ProductBaseView, View):
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
    

class AddProductView(ProductBaseView, View):
    success_url = reverse_lazy('users:products')
    redirect_url = success_url

    def post(self, request, *args, **kwargs):
        center = super().get_object()

        products = request.POST.getlist('products')

        for product in products:
            center.products.add(product)
            center.save()
        
        messages.success(request, 'Added Products')
        return redirect(self.success_url)
    

class ProductEnquiryListView(ProductBaseView, ListView):
    model = ProductEnquiry
    template_name = 'user_products/enquiry_list.html'
    context_object_name = 'enquiries'

    def get_queryset(self):
        center = CscCenter.objects.filter(email = self.request.user.email).first()
        enquiries = self.model.objects.filter(csc_center = center).order_by('-created')
        return enquiries
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enquiries'] = self.get_queryset()
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            center_slug = request.GET.get('center_slug')
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)
                enquiries = self.model.objects.filter(csc_center = center)
                enquiries_list = []
                for count, enquiry in enumerate(enquiries):
                    enquiries_list.append({'applicant_name': enquiry.applicant_name, 'applicant_email': enquiry.applicant_email, 'applicant_phone': enquiry.applicant_phone, 'get_absolute_url': enquiry.get_absolute_url, 'product': enquiry.product.name, 'count': count+1})
                return JsonResponse({'enquiries': enquiries_list})
            except Http404:
                pass
        return super().get(request, *args, **kwargs)
    

class ProductEnquiryDetailView(ProductBaseView, DetailView):
    model = ProductEnquiry
    template_name = 'user_products/enquiry_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'enquiry'
    
    def get_object(self, **kwargs):
        try:
            self.object = get_object_or_404(ProductEnquiry, slug = self.kwargs['slug'])
            return self.object
        except Http404:
            return redirect(reverse_lazy('users:enquiries'))
    

class DeleteProductEnquiryView(ProductBaseView, View):
    model = ProductEnquiry
    success_url = reverse_lazy('users:enquiries')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(ProductEnquiry, slug = self.kwargs['slug'])
        except Http404:
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(self.request, 'Enquiry deleted successfully')
        return redirect(self.success_url)

# CSC Centers2
class CscCenterBaseView(BaseUserView):
    model = CscCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['center_page'] = True
        return context

class CscCenterListView(CscCenterBaseView, ListView):
    template_name = 'user_csc_center/list.html'
    context_object_name = 'centers'

    def get_queryset(self):
        return CscCenter.objects.filter(email = self.request.user.email)
    

class AddCscCenterView(CscCenterBaseView, CreateView):
    template_name = 'user_csc_center/create.html'
    success_url = reverse_lazy('users:add_csc')
    redirect_url = success_url
    fields = "__all__"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_types'] = CscNameType.objects.all().order_by('type')
        context['keywords'] = CscKeyword.objects.all().order_by('keyword')
        context['products'] = Product.objects.all()
        context['services'] = Service.objects.all()
        context['states'] = State.objects.all()
        context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]

        time_data = []
        for i in range(1, 25):
            if i < 13:
                str_time = f"{i} AM"
            else:
                str_time = f"{i-12} PM"            
            time = datetime.strptime(str_time, "%I %p").strftime("%H:%M")
            time_data.append({"str_time": str_time, "time": time})
            context['time_data'] = time_data

        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        type = request.POST.get('type')
        keywords = request.POST.getlist('keywords')

        state = request.POST.get('state')
        district = request.POST.get('district')
        block = request.POST.get('block')
        location = request.POST.get('location')
        zipcode = request.POST.get('zipcode')
        landmark_or_building_name = request.POST.get('landmark_or_building_name')
        street = request.POST.get('address')
        logo = request.FILES.get('logo') # dropzone
        banner = request.FILES.get('banner') # dropzone
        description = request.POST.get('description')
        contact_number = request.POST.get('contact_number')
        mobile_number = request.POST.get('mobile_number')
        whatsapp_number = request.POST.get('whatsapp_number')
        email = request.POST.get('email')
        website = request.POST.get('website') # optional
        services = request.POST.getlist('services')
        products = request.POST.getlist('products')

        show_opening_hours = request.POST.get('show_opening_hours')

        mon_opening_time = request.POST.get('mon_opening_time') if show_opening_hours else None #timefield
        tue_opening_time = request.POST.get('tue_opening_time') if show_opening_hours else None #timefield
        wed_opening_time = request.POST.get('wed_opening_time') if show_opening_hours else None #timefield
        thu_opening_time = request.POST.get('thu_opening_time') if show_opening_hours else None #timefield
        fri_opening_time = request.POST.get('fri_opening_time') if show_opening_hours else None #timefield
        sat_opening_time = request.POST.get('sat_opening_time') if show_opening_hours else None #timefield
        sun_opening_time = request.POST.get('sun_opening_time') if show_opening_hours else None #timefield

        mon_closing_time = request.POST.get('mon_closing_time') if show_opening_hours else None #timefield
        tue_closing_time = request.POST.get('tue_closing_time') if show_opening_hours else None #timefield
        wed_closing_time = request.POST.get('wed_closing_time') if show_opening_hours else None #timefield
        thu_closing_time = request.POST.get('thu_closing_time') if show_opening_hours else None #timefield
        fri_closing_time = request.POST.get('fri_closing_time') if show_opening_hours else None #timefield
        sat_closing_time = request.POST.get('sat_closing_time') if show_opening_hours else None #timefield
        sun_closing_time = request.POST.get('sun_closing_time') if show_opening_hours else None #timefield

        mon_opening_time = mon_opening_time if  mon_opening_time != "" else None
        tue_opening_time = tue_opening_time if  tue_opening_time != "" else None
        wed_opening_time = wed_opening_time if  wed_opening_time != "" else None
        thu_opening_time = thu_opening_time if  thu_opening_time != "" else None
        fri_opening_time = fri_opening_time if  fri_opening_time != "" else None
        sat_opening_time = sat_opening_time if  sat_opening_time != "" else None
        sun_opening_time = sun_opening_time if  sun_opening_time != "" else None
         
        mon_closing_time = mon_closing_time if  mon_closing_time != "" else None
        tue_closing_time = tue_closing_time if  tue_closing_time != "" else None
        wed_closing_time = wed_closing_time if  wed_closing_time != "" else None
        thu_closing_time = thu_closing_time if  thu_closing_time != "" else None
        fri_closing_time = fri_closing_time if  fri_closing_time != "" else None
        sat_closing_time = sat_closing_time if  sat_closing_time != "" else None
        sun_closing_time = sun_closing_time if  sun_closing_time != "" else None

        show_social_media_links = request.POST.get('show_social_media_links')

        social_medias = request.POST.getlist('social_medias') if show_social_media_links else None # manytomany
        social_links = request.POST.getlist('social_links') if show_social_media_links else None # manytomany

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        try:
            type = get_object_or_404(CscNameType, slug = type)
        except Http404:
            messages.error(request, 'Invalid CSC Name Type')
            return redirect(self.redirect_url)

        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            messages.error(request, 'Invalid State')
            return redirect(self.redirect_url)

        try:
            district = get_object_or_404(District, pk = district)
        except Http404:
            messages.error(request, 'Invalid District')
            return redirect(self.redirect_url)
        
        try:
            block = get_object_or_404(Block, pk = block)
        except Http404:
            messages.error(request, 'Invalid Block')
            return redirect(self.redirect_url)
        
        self.object = CscCenter.objects.create(
            name = name, type = type, state = state,
            district = district,block = block,location = location,
            zipcode = zipcode, landmark_or_building_name = landmark_or_building_name,
            street = street, logo = logo, banner = banner,
            description = description, contact_number = contact_number,
            mobile_number = mobile_number, whatsapp_number = whatsapp_number,
            email = email, website = website, mon_opening_time = mon_opening_time, 
            tue_opening_time = tue_opening_time, wed_opening_time = wed_opening_time, 
            thu_opening_time = thu_opening_time, fri_opening_time = fri_opening_time, 
            sat_opening_time = sat_opening_time, sun_opening_time = sun_opening_time, 
            mon_closing_time = mon_closing_time,tue_closing_time = tue_closing_time,
            wed_closing_time = wed_closing_time,thu_closing_time = thu_closing_time,
            fri_closing_time = fri_closing_time,sat_closing_time = sat_closing_time,
            sun_closing_time = sun_closing_time, latitude = latitude,
            longitude = longitude
        )

        messages.success(request, "Added CSC center")      
        
        # after creation of object
        self.object.keywords.set(keywords)
        self.object.services.set(services)
        self.object.products.set(products)
        self.object.save()

        if social_medias and social_links:
            social_media_length = len(social_medias)
            if social_media_length > 0:
                social_media_list = []
                for i in range(social_media_length):
                    if social_medias[i] and social_links[i]:
                        social_media_link, created = SocialMediaLink.objects.get_or_create(
                            csc_center_id = self.object,
                            social_media_name = social_medias[i],
                            social_media_link = social_links[i]
                        )
                        social_media_list.append(social_media_link)
                
                    self.object.social_media_links.set(social_media_list)
                    self.object.save()
        
        return redirect(self.success_url)
        