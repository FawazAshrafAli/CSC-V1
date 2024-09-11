from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from datetime import datetime
from django.http import Http404

from .models import CscCenter, CscKeyword, CscNameType, State, District, Block, SocialMediaLink, Banner
from services.models import Service
from products.models import Product
from authentication.models import User


class AddCscCenterView(CreateView):
    template_name = 'csc_center/add.html'
    success_url = reverse_lazy('authentication:login')
    redirect_url = success_url
    fields = "__all__"
    
    def get_context_data(self, **kwargs):
        context = {}
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
        banners = request.FILES.getlist('banner') # dropzone
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
            street = street, logo = logo,
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
        
        # after creation of object
        self.object.keywords.set(keywords)
        self.object.services.set(services)
        self.object.products.set(products)
        self.object.save()

        if banners:
            for banner in banners:
                banner_obj, created = Banner.objects.get_or_create(csc_center = self.object, banner_image = banner)
                self.object.banners.add(banner_obj)
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


        messages.success(request, "Added CSC center")
        if not User.objects.filter(email = email).exists():            
            return redirect(reverse('authentication:user_registration', kwargs={'email': self.object.email}))
        
        
        return redirect(self.success_url)