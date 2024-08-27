from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View, CreateView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.contrib.auth import authenticate, logout
from django.views.decorators.csrf import csrf_exempt
import base64

from posters.forms import PosterFooterTextForm

from authentication.models import User
from posters.models import Poster, CustomPoster
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
            context['services_left'] = Service.objects.all()
            context['user_csc_centers'] = CscCenter.objects.filter(email = self.request.user.email)

        except Exception as e:
            print(e)
            pass

        return context
    

class HomeView(BaseUserView, TemplateView):
    template_name = 'user_home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        csc_center = CscCenter.objects.filter(email = self.request.user.email).first()

        center_slug = self.request.GET.get('center_slug')        
        if center_slug:
            try:
                csc_center = get_object_or_404(CscCenter, slug = center_slug)
            except Http404:
                pass

        context["csc_center"] = csc_center
        context["service_enquiries"] = ServiceEnquiry.objects.filter(csc_center = csc_center, is_viewed = False).order_by('-created')
        context["product_enquiries"] = ProductEnquiry.objects.filter(csc_center = csc_center, is_viewed = False).order_by('-created')
        context["home_page"] = True
        return context

class GetCenterDataView(BaseUserView, View):
    def get(self, request, *args, **kwargs):
        center_slug = request.GET.get('center_slug')

        try:
            center = get_object_or_404(CscCenter, slug = center_slug)
            print(center)
        except Http404:
            pass

        service_enquiries = ServiceEnquiry.objects.filter(csc_center = center, is_viewed = False)
        product_enquiries = ProductEnquiry.objects.filter(csc_center = center, is_viewed = False)

        service_enquiry_list = []
        for enquiry in service_enquiries:
            service_enquiry_list.append({
                "applicant_name": enquiry.applicant_name,
                "service": enquiry.service.first_name,
                "get_absolute_url": enquiry.get_absolute_url,
                "slug": enquiry.slug
            })

        product_enquiry_list = []
        for enquiry in product_enquiries:
            product_enquiry_list.append({
                "applicant_name": enquiry.applicant_name,
                "product": enquiry.product.name,
                "get_absolute_url": enquiry.get_absolute_url,
                "slug": enquiry.slug
            })

        data = {
            'services_count': center.services.all().count(),
            'products_count': center.products.all().count(),
            "service_enquiries_count" : service_enquiries.count(),
            "product_enquiries_count" : product_enquiries.count(),
            'service_enquiries': service_enquiry_list,
            'product_enquiries': product_enquiry_list
            }

        return JsonResponse(data)


# Service
class BaseServiceView(BaseUserView):
    model = CscCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context


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
                    enquiries_list.append({
                        'applicant_name': enquiry.applicant_name, 
                        'applicant_email': enquiry.applicant_email, 
                        'applicant_phone': enquiry.applicant_phone, 
                        'get_absolute_url': enquiry.get_absolute_url if enquiry.get_absolute_url else None,
                        'service': enquiry.service.first_name, 
                        'slug': enquiry.slug, 'count': count+1})
                return JsonResponse({'enquiries': enquiries_list})
            except Http404:
                pass
        return super().get(request, *args, **kwargs)
    

class ServiceEnquiryDetailView(BaseServiceView, DetailView):
    model = ServiceEnquiry
    template_name = 'user_services/enquiry_detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'enquiry'
    
    def get_object(self):
        try:
            enquiry = get_object_or_404(ServiceEnquiry, slug = self.kwargs['slug'])
            enquiry.is_viewed = True
            enquiry.save()
            return enquiry
        except Http404:
            return redirect(reverse_lazy('users:service_enquiries'))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enquiry'] = self.get_object()
        return context

    
@method_decorator(csrf_exempt, name='dispatch')
class MarkServiceEnquiryAsViewedView(BaseServiceView, UpdateView):
    model = ServiceEnquiry

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_viewed = True
        self.object.save()

        service_enquiries = ServiceEnquiry.objects.filter(csc_center = self.object.csc_center, is_viewed = False)

        service_enquiry_list = []
        for enquiry in service_enquiries:
            service_enquiry_list.append({
                "applicant_name": enquiry.applicant_name,
                "service": enquiry.service.first_name,
                "get_absolute_url": enquiry.get_absolute_url,
            })

        return JsonResponse({'service_enquiries': service_enquiry_list})



class DeleteServiceEnquiryView(BaseServiceView, View):
    model = ServiceEnquiry
    success_url = reverse_lazy('users:service_enquiries')
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
    model = CscCenter
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_page'] = True
        context['products'] = Product.objects.all()
        return context  
    

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
                    enquiries_list.append({
                        'applicant_name': enquiry.applicant_name, 
                        'applicant_email': enquiry.applicant_email, 
                        'applicant_phone': enquiry.applicant_phone, 
                        'get_absolute_url': enquiry.get_absolute_url, 
                        'product': enquiry.product.name, 
                        'slug': enquiry.slug, 
                        'count': count+1})
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
            enquiry = get_object_or_404(ProductEnquiry, slug = self.kwargs['slug'])
            enquiry.is_viewed = True
            enquiry.save()
            return enquiry
        except Http404:
            return redirect(reverse_lazy('users:product_enquiries'))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enquiry'] = self.get_object()
        return context
    

@method_decorator(csrf_exempt, name='dispatch')
class MarkProductEnquiryAsViewedView(ProductBaseView, UpdateView):
    model = ProductEnquiry

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_viewed = True
        self.object.save()

        product_enquiries = ProductEnquiry.objects.filter(csc_center = self.object.center, is_viewed = False)

        product_enquiry_list = []
        for enquiry in product_enquiries:
            product_enquiry_list.append({
                "applicant_name": enquiry.applicant_name,
                "product": enquiry.product.first_name,
                "get_absolute_url": enquiry.get_absolute_url,
            })

        return JsonResponse({'product_enquiries': product_enquiry_list})


class DeleteProductEnquiryView(ProductBaseView, View):
    model = ProductEnquiry
    success_url = reverse_lazy('users:product_enquiries')
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
    

class GetCurrentCscCenterView(CscCenterBaseView, View):
    def get(self, request, *args, **kwargs):
        center_slug = request.GET.get('center_slug')

        try:
            center = get_object_or_404(CscCenter, slug = center_slug)
            data = {
                'current_center_logo': center.logo.url if center.logo else None,
                'current_center_name': center.name
                }

            return JsonResponse(data)
        except Http404:
            pass
            

class CscCenterListView(CscCenterBaseView, ListView):
    template_name = 'user_csc_center/list.html'
    context_object_name = 'centers'

    def get_queryset(self):
        return CscCenter.objects.filter(email = self.request.user.email)
    

class DetailCscCenterView(CscCenterBaseView, DetailView):
    template_name = "user_csc_center/detail.html"
    context_object_name = 'center_obj'
    slug_url_kwarg = 'slug'

    def get_object(self):
        try:
            return get_object_or_404(CscCenter, slug = self.kwargs['slug'])
        except Http404:
            messages.error(self.request, 'Invalid CSC center')
            return redirect(reverse_lazy('user:csc_centers'))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['center_obj'] = self.get_object()
        return context
    

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
        owner = request.POST.get('owner')
        email = request.POST.get('email')
        website = request.POST.get('website') # optional
        contact_number = request.POST.get('contact_number')
        mobile_number = request.POST.get('mobile_number')
        whatsapp_number = request.POST.get('whatsapp_number')        
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
            mobile_number = mobile_number, whatsapp_number = whatsapp_number, owner = owner,
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

        if not User.objects.filter(email = email).exists():
            User.objects.create_user(username = email, email = email, password = contact_number)

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
    

@method_decorator(never_cache, name="dispatch")
class UpdateCscCenterView(CscCenterBaseView, UpdateView):
    model = CscCenter
    template_name = 'user_csc_center/update.html'
    context_object_name = 'center_obj'
    fields = "__all__"
    slug_url_kwarg = 'slug'

    def get_object(self, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs['slug'])
            return self.object
        except Http404:
            messages.error(self.request, "Invalid CSC center")
            return redirect(reverse_lazy('users:csc_centers'))
        
    def get_success_url(self):
        return reverse_lazy('users:csc_center', kwargs = {'slug': self.kwargs.get('slug')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_types'] = CscNameType.objects.all().order_by('type')
        context['keywords'] = CscKeyword.objects.all().order_by('keyword')
        context['products'] = Product.objects.all()
        context['states'] = State.objects.all()
        context['services'] = Service.objects.all()
        context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]
        self.object = self.get_object()
        context['center_obj'] = self.object
        context['selected_districts'] = District.objects.filter(state = self.object.state)
        context['selected_blocks'] = Block.objects.filter(district = self.object.district)

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
        owner = request.POST.get('owner')
        email = request.POST.get('email')
        website = request.POST.get('website') # optional
        contact_number = request.POST.get('contact_number')
        mobile_number = request.POST.get('mobile_number')
        whatsapp_number = request.POST.get('whatsapp_number')        
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
            return redirect(reverse_lazy('users:add_csc'))

        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            messages.error(request, 'Invalid State')
            return redirect(reverse_lazy('users:add_csc'))

        try:
            district = get_object_or_404(District, pk = district)
        except Http404:
            messages.error(request, 'Invalid District')
            return redirect(reverse_lazy('users:add_csc'))
        
        try:
            block = get_object_or_404(Block, pk = block)
        except Http404:
            messages.error(request, 'Invalid Block')
            return redirect(reverse_lazy('users:add_csc'))
        
        self.object = self.get_object()

        self.object.name = name
        self.object.type = type
        self.object.state = state
        self.object.district = district
        self.object.block = block
        self.object.location = location
        self.object.zipcode = zipcode
        self.object.landmark_or_building_name = landmark_or_building_name
        self.object.street = street

        if not logo:
            logo = self.object.logo
        self.object.logo = logo

        if not banner:
            banner = self.object.banner
        self.object.banner = banner

        self.object.description = description
        self.object.owner = owner
        self.object.email = email
        self.object.website = website
        self.object.contact_number = contact_number
        self.object.mobile_number = mobile_number
        self.object.whatsapp_number = whatsapp_number

        self.object.show_opening_hours = True if show_opening_hours else False
        self.object.show_social_media_links = True if show_social_media_links else False

        self.object.mon_opening_time = mon_opening_time
        self.object.tue_opening_time = tue_opening_time
        self.object.wed_opening_time = wed_opening_time
        self.object.thu_opening_time = thu_opening_time
        self.object.fri_opening_time = fri_opening_time
        self.object.sat_opening_time = sat_opening_time
        self.object.sun_opening_time = sun_opening_time
        self.object.mon_closing_time = mon_closing_time
        self.object.tue_closing_time = tue_closing_time
        self.object.wed_closing_time = wed_closing_time
        self.object.thu_closing_time = thu_closing_time
        self.object.fri_closing_time = fri_closing_time
        self.object.sat_closing_time = sat_closing_time
        self.object.sun_closing_time = sun_closing_time

        self.object.latitude = latitude
        self.object.longitude = longitude
        
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
            else:
                self.object.social_media_links.clear()
                self.object.save()
        else:
            self.object.social_media_links.clear()
            self.object.save()

        messages.success(request, "Updated CSC Center Details")      
        
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field - {field}: {error}")
        return super().form_invalid(form)
        


###################### Posters ################################

class BasePosterView(BaseUserView, View):
    model = Poster
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poster_page'] = True
        if CscCenter.objects.filter(email = self.request.user.email).count() > 1:
            context['multi_center_owner'] = True
        return context


class AvailablePosterView(BasePosterView, ListView):
    queryset = Poster.objects.all()
    context_object_name = 'posters'
    template_name = "user_posters/available_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context[f"{self.context_object_name}"] = self.queryset        
        return context


class MyPosterListView(BasePosterView, ListView):
    context_object_name = 'posters'
    template_name = "user_posters/my_list.html"

    def get_queryset(self):
        csc_center = CscCenter.objects.filter(email = self.request.user.email).first()
        return CustomPoster.objects.filter(csc_center = csc_center)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[f"{self.context_object_name}"] = self.get_queryset()
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            center_slug = request.GET.get('center_slug')
            try:
                center = get_object_or_404(CscCenter, slug = center_slug, email = request.user.email)

                posters = CustomPoster.objects.filter(csc_center = center)

                poster_list = []
                for count, poster in enumerate(posters):
                    poster_list.append({
                        'title': poster.title, 
                        'poster': poster.poster.url if poster.poster else None, 
                        'slug': poster.slug, 
                        'count': count+1,
                        'get_absolute_url': poster.get_absolute_url if poster.get_absolute_url else '#',
                        })
                return JsonResponse({'posters': poster_list})
            except Http404:
                pass
        return super().get(request, *args, **kwargs)

    
class MyPosterDetailView(BasePosterView, DetailView):
    model = CustomPoster
    context_object_name = 'poster'
    template_name = "user_posters/my_detail.html"
    success_url = reverse_lazy('users:my_posters')
    redirect_url = success_url
    slug_url_kwarg = 'slug'

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Poster")
            return redirect(self.redirect_url)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poster'] = self.get_object()
        return context


class CreatePosterView(BasePosterView, CreateView):
    template_name = "user_posters/create.html"
    success_url = reverse_lazy('users:available_posters')
    redirect_url = success_url

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(self.model, slug = self.kwargs['slug'])
        except Http404:
            return redirect(self.redirect_url)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poster'] = self.get_object()
        context['form'] = PosterFooterTextForm()        
        return context

    # def get(self, request, *args, **kwargs):
    #     poster = self.get_object()
    #     context = self.get_context_data(**kwargs)
    #     return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        form = PosterFooterTextForm()

        if form.is_valid():
            text = form.cleaned_data['text']
            # self.object.description = description
            # self.object.save()
        else:
            form = PosterFooterTextForm()
        # self.object.save()

        messages.success(request, 'Updated Poster')
        return redirect(self.get_success_url())


class GetQrCodeView(BasePosterView, DetailView):
    model = CscCenter

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        qr_code = self.object.qr_code_image.url
        center = self.object.name

        return JsonResponse({'qr_code': qr_code, 'center': center})


class SavePosterView(BasePosterView, View):
    success_url = reverse_lazy('users:my_posters')
    redirect_url = reverse_lazy('users:available_posters')
    
    def post(self, request, *args, **kwargs):
        try:
            image = request.POST.get('image')
            title =request.POST.get('title')
            description = request.POST.get('description')
            if CscCenter.objects.filter(email = request.user.email).count() > 1:
                csc_center = request.POST.get('csc_center')
                try:
                    csc_center = get_object_or_404(CscCenter, slug = csc_center)
                except Http404:
                    return JsonResponse({"message": "Invalid csc center"})
            else:
                csc_center = CscCenter.objects.filter(email = request.user.email).first()

            format, imgstr = image.split(';base64,')
            # ext = format.split('/')[-1]  # Get the file extension (e.g., 'png')
            ext = 'jpg'

            # Decode the base64 string
            image = ContentFile(base64.b64decode(imgstr), name='my_1poster_image.' + ext)

            CustomPoster.objects.create(csc_center = csc_center, poster = image, title = title, description = description)

            return JsonResponse({'message': 'Success', 'success_url': '/users/my_posters'})
        except Exception as e:
            print(f"Exception: {e}")
            return JsonResponse({"message": 'Poster creation failed'})


class DeleteMyPosterView(BasePosterView, View):
    success_url = reverse_lazy('users:my_posters')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(CustomPoster, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid poster")
            return redirect(self.redirect_url)
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, "Deleted Poster")
        return redirect(self.success_url)
    

class DownloadPosterView(BasePosterView, View):
    model = CustomPoster

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.poster:
            image_file = self.object.poster.file
            image_content = image_file.read()

            response = HttpResponse(image_content, content_type='image/jpeg')

            response['Content-Disposition'] = f'attachment; filename="{self.object.title}.jpg"'
            
            return response
        


########## Poster End ##########

########## My Profile Start ##########

class BaseMyProfileView(BaseUserView, View):
    model = User


class MyProfileView(BaseMyProfileView, TemplateView):
    template_name = 'user_profile/my_profile.html'
    redirect_url = reverse_lazy('authentication:login')

    def get_object(self):
        try:
            return get_object_or_404(self.model, email = self.request.user.email)
        except Http404:
            return redirect(self.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.get_object()
        return context
    

class UpdateProfileView(MyProfileView, UpdateView):
    success_url = reverse_lazy('users:my_profile')
    redirect_url = success_url
    
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            image = request.FILES.get('image')
            name = request.POST.get('name').strip().title()
            phone = request.POST.get('phone').strip()
            email = request.POST.get('email').strip().lower()
            notes = request.POST.get('notes').strip()
            twitter = request.POST.get('twitter').strip().lower()
            facebook = request.POST.get('facebook').strip().lower()
            google = request.POST.get('google').strip().lower()

            required_fields = {
                "Name": name,
                "Phone": phone,
                "Email": email
            }

            for field_name, field_value in required_fields.items():
                if not field_value:
                    messages.error(request, f"{field_name} is required")
                    return redirect(self.redirect_url)

            name_parts = name.split(' ')

            first_name = name_parts[0] if len(name_parts) > 0 else None
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else None

            self.object.first_name = first_name
            self.object.last_name = last_name            
            self.object.notes = notes
            self.object.twitter = twitter
            self.object.facebook = facebook
            self.object.google = google

            
            if  phone.isnumeric():
                self.object.phone = phone
            
            if image:
                self.object.image = image

            self.object.save()

            current_email = self.object.email

            if email != current_email:
                user_csc_centers = CscCenter.objects.filter(email = current_email)
                for csc_center in user_csc_centers:
                    csc_center.email = email
                    csc_center.save()
                self.object.email = email
                self.object.save()

            messages.success(request, "Updated user profile details.")
            return redirect(self.get_success_url())
        except Exception as e:
            print(f"Exception: {e}")
            return redirect(self.redirect_url)
        

class ChangePasswordView(MyProfileView, UpdateView):
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy('users:my_profile')

    def get_object(self):
        try:
            return get_object_or_404(User, username = 'admin')
        except Http404:
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            user = authenticate(request, username = request.user.username, password = current_password)

            if user is not None and new_password == confirm_password:
                self.object.set_password(new_password)
                self.object.save()
                messages.success(request, "Password Updated. Please login again with your new password")
                logout(request)
                return redirect(self.get_success_url())
            
            if user is None:
                error_msg = "The current password you entered is incorrect"
            elif new_password != confirm_password:
                error_msg = "New passwords are not matching"
            else:
                error_msg = "Something went wrong."

            messages.error(request, error_msg)
            return redirect(self.redirect_url)
        
        except Exception as e:
            print(f"Exception: {e}")
            return redirect(self.redirect_url)
