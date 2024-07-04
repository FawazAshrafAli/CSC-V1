import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.views.generic import TemplateView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from .models import Block
from .models import CommonServiceCenter as CSC
from services.models import Service


class HomePageView(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = Service.objects.all()
        return context
    


@method_decorator(never_cache, name="dispatch")
class FilteredLocationView(View):
    def get(self, request, *args, **kwargs):
        state = request.GET.get('state', None)
        district = request.GET.get('district', None)
        block = request.GET.get('block', None)


        response_data = {}
        print(district)
        if state and district and block:
            centers = CSC.objects.filter(state__state = state, district__district = district, block__block = block)
        elif state and district:
            centers = CSC.objects.filter(state__state = state, district__district = district)
        elif state:
            centers = CSC.objects.filter(state__state = state)
            
        else:
            message = "Please choose atleast one filtering."
            response_data['message'] = message

        if centers:
            response_data.update({
                'centers_data': list(centers.values()),
                'block': block
                })

        return JsonResponse(response_data, safe=False)

@method_decorator(never_cache, name="dispatch")
class PincodeLocationView(View):
    def get(self, request, *args, **kwargs):
        pincode = request.GET.get('pincode', None)

        response_data = {}
        if pincode:
            api_key = '1b4ea0d7dc5f4cffb9dbd971a896a71c'

            url = f'https://api.opencagedata.com/geocode/v1/json?q={pincode}&key={api_key}'

            response = requests.get(url)
            data = response.json()

            if data['results']:
                county = data['results'][0]['components']['county']
                latitude = data['results'][0]['geometry']['lat']
                longitude = data['results'][0]['geometry']['lng']
                response_data.update({
                    'place': county,
                })
                if county:
                    block = Block.objects.get(block = county)
                    centers = CSC.objects.filter(block = block)
                    response_data['centers_data'] = list(centers.values())
            else:
                response_data.update({
                    'message': f"No location found for pincode {pincode}"
                })
                print(f"No location found for pincode {pincode}")

        else:
            response_data.update({'message': "No data available for this pincode."})

        return JsonResponse(response_data, safe=False, status=200)    




@method_decorator(never_cache, name="dispatch")
class LocateMeView(View):
    def get(self, request, *args, **kwargs):
        latitude = request.GET.get('latitude', None)
        longitude = request.GET.get('longitude', None)

        response_data = {}
        if latitude and longitude:
            api_key = '1b4ea0d7dc5f4cffb9dbd971a896a71c'

            url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}'

            response = requests.get(url)
            data = response.json()

            if data['results']:
                county = data['results'][0]['components']['county']
                response_data.update({
                    'place': county,
                })
                print(f"The county for the given coordinates is {county}")

                if county:
                    try:
                        block = get_object_or_404(Block, block = county)
                        centers = CSC.objects.filter(block = block)
                        response_data['centers_data'] = list(centers.values())
                    except Http404:
                        pass
                
            else:
                response_data.update({
                    'message': f"No location found for the given coordinates."
                })
                print(f"No location found for the given coordinates.")

        else:
            response_data.update({'message': "Please provide both latitude and longitude."})

        return JsonResponse(response_data, safe=False, status=200)
    


# Detail CSC Center

class DetailCscView(DetailView):
    model = CSC
    template_name = 'csc/detail_csc.html'
    context_object_name = 'csc'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        services = self.object.service.all()
        context['services'] = services
        return context
