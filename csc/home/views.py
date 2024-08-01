import requests
from django.shortcuts import redirect, get_object_or_404, render
from django.http import JsonResponse, Http404
from django.views.generic import TemplateView, View, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.paginator import Paginator

from csc_center.models import CscCenter, State, District, Block
from services.models import Service


class HomePageView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = {}
        context["services"] = Service.objects.all()
        context['states'] = State.objects.all()
        return context
    

# @method_decorator(never_cache, name="dispatch")
# class FilteredLocationView(View):
#     def get(self, request, *args, **kwargs):
#         state = request.GET.get('state', None)
#         district = request.GET.get('district', None)
#         block = request.GET.get('block', None)


#         response_data = {}
#         print(district)
#         if state and district and block:
#             centers = CscCenter.objects.filter(state__state = state, district__district = district, block__block = block)
#         elif state and district:
#             centers = CscCenter.objects.filter(state__state = state, district__district = district)
#         elif state:
#             centers = CscCenter.objects.filter(state__state = state)
            
#         else:
#             message = "Please choose atleast one filtering."
#             response_data['message'] = message

#         if centers:
#             response_data.update({
#                 'centers_data': list(centers.values()),
#                 'block': block
#                 })

#         return JsonResponse(response_data, safe=False)

# @method_decorator(never_cache, name="dispatch")
# class PincodeLocationView(View):
#     def get(self, request, *args, **kwargs):
#         pincode = request.GET.get('pincode', None)

#         response_data = {}
#         if pincode:
#             api_key = '1b4ea0d7dc5f4cffb9dbd971a896a71c'

#             url = f'https://api.opencagedata.com/geocode/v1/json?q={pincode}&key={api_key}'

#             response = requests.get(url)
#             data = response.json()

#             if data['results']:
#                 county = data['results'][0]['components']['county']
#                 latitude = data['results'][0]['geometry']['lat']
#                 longitude = data['results'][0]['geometry']['lng']
#                 response_data.update({
#                     'place': county,
#                 })
#                 if county:
#                     block = Block.objects.get(block = county)
#                     centers = CscCenter.objects.filter(block = block)
#                     response_data['centers_data'] = list(centers.values())
#             else:
#                 response_data.update({
#                     'message': f"No location found for pincode {pincode}"
#                 })
#                 print(f"No location found for pincode {pincode}")

#         else:
#             response_data.update({'message': "No data available for this pincode."})

#         return JsonResponse(response_data, safe=False, status=200)    




# @method_decorator(never_cache, name="dispatch")
# class LocateMeView(View):
#     def get(self, request, *args, **kwargs):
#         latitude = request.GET.get('latitude', None)
#         longitude = request.GET.get('longitude', None)

#         response_data = {}
#         if latitude and longitude:
#             api_key = '1b4ea0d7dc5f4cffb9dbd971a896a71c'

#             url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}'

#             response = requests.get(url)
#             data = response.json()

#             if data['results']:
#                 county = data['results'][0]['components']['county']
#                 response_data.update({
#                     'place': county,
#                 })
#                 print(f"The county for the given coordinates is {county}")

#                 if county:
#                     try:
#                         block = get_object_or_404(Block, block = county)
#                         centers = CscCenter.objects.filter(block = block)
#                         response_data['centers_data'] = list(centers.values())
#                     except Http404:
#                         pass
                
#             else:
#                 response_data.update({
#                     'message': f"No location found for the given coordinates."
#                 })
#                 print(f"No location found for the given coordinates.")

#         else:
#             response_data.update({'message': "Please provide both latitude and longitude."})

#         return JsonResponse(response_data, safe=False, status=200)
    


# Detail CscCenter Center
class DetailCscView(DetailView):
    model = CscCenter
    template_name = 'csc/detail_csc.html'
    context_object_name = 'csc'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        services = self.object.services.all()
        context['services'] = services
        return context
    


class SearchCscCenterView(HomePageView, ListView):
    model = CscCenter
    template_name = 'home/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def initial(self, request, *args, **kwargs):
        state = request.GET.get('state', None)
        district = request.GET.get('district', None)
        block = request.GET.get('block', None)

        if state:
            try:
                state = get_object_or_404(State, pk=state)
                kwargs['state'] = state
            except Http404:
                pass

        if district:
            try:
                district = get_object_or_404(District, pk=district)
                kwargs['district'] = district
            except Http404:
                pass

        if block:
            try:
                block = get_object_or_404(Block, pk=block)
                kwargs['block'] = block
            except Http404:
                pass

        centers = CscCenter.objects.filter(**kwargs)

        if block:
            location = block
        elif district:
           location = district
        elif state:
            location = state
        else:
            location = None

        context = self.get_context_data(**kwargs)

        context.update({
            'state_obj': state if state else None,
            'district_obj': district if district else None,
            'block_obj': block if block else None,
            'location': location,
            'districts': District.objects.filter(state = state) if state else None,
            'blocks': Block.objects.filter(state = state, district = district) if state and district else None,
            })

        return centers, context
    
    def get(self, request, *args, **kwargs):
        centers, context = self.initial(request, *args, **kwargs)
        centers = centers.order_by('name')
        context.update({
            'centers': centers,            
            })
        return render(request, self.template_name, context)


class FilterAndSortCscCenterView(SearchCscCenterView):
    def get(self, request, *args, **kwargs):
        services = request.GET.getlist('services[]', None)
        listing = request.GET.get('listing', None)

        centers, context = self.initial(request, *args, **kwargs)

        filtered_centers = centers

        for center in centers:
            set_services = set()
            for service in center.services.all():
                set_services.add(service.slug)
            if not set(services).issubset(set_services):
                filtered_centers = filtered_centers.exclude(pk=center.pk)

        filtered_centers = filtered_centers.order_by(listing)

        list_centers = []
        for center in filtered_centers:
            list_centers.append({
                "pk": center.pk,
                "full_name": center.full_name,
                "logo": center.logo.url if center.logo
                 else None,
                "partial_address": center.partial_address
            })

        data = {
            'message': 'success',
            "centers": list_centers,
        }

        return JsonResponse(data)


# class PaginationCscCenterView(SearchCscCenterView):
#     def get(self, request, *args, **kwargs):
#         centers = self.initial(request, *args, **kwargs)

#         list_centers = []
#         for center in centers:
#             list_centers.append({
#                 "pk": center.pk,
#                 "full_name": center.full_name,
#                 "logo": center.logo.url if center.logo else None,
#                 "partial_address": center.partial_address
#             })

#         data = {
#             'centers': list_centers,
#             'has_next': centers.has_next(),
#             'has_previous': centers.has_previous(),
#             'next_page_number': centers.next_page_number() if centers.has_next() else None,
#             'previous_page_number': centers.previous_page_number() if centers.has_previous() else None
#         }

#         return JsonResponse(data)

class CscCenterDetailView(DetailView):
    model = CscCenter
    template_name = 'home/detail.html'
    context_object_name = 'center'
    slug_url_kwarg = 'slug'

