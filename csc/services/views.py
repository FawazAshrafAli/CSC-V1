from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View, CreateView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib import messages

from .models import Service
from csc_admin.models import ServiceEnquiry

class BaseServiceView:
    model = Service
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        context['service_page'] = True
        return context

@method_decorator(never_cache, name="dispatch")
class ListServiceView(BaseServiceView, ListView):
    queryset = Service.objects.all()
    template_name = 'services/list.html'
    context_object_name = "services"


@method_decorator(never_cache, name="dispatch")
class DetailServiceView(BaseServiceView, DetailView):
    template_name = 'services/detail.html'
    context_object_name = "service"
    slug_url_kwarg = 'slug'


# Create Service Enquiry (To super admin)
class CreateServiceEnquiryView(DetailServiceView, CreateView):
    redirect_url = reverse_lazy('services:services')

    def get_success_url(self):
        try:
            return reverse_lazy('services:service', kwargs={'slug': self.kwargs['slug']})
        except Exception as e:
            messages.error(self.request, "Something went wrong")
            return redirect(self.redirect_url)
        
    def get_redirect_url(self):
        return self.get_success_url()
    
    def post(self, request, *args, **kwargs):
        service = self.get_object()
        print(f"The service is: {service}")

        applicant_name = request.POST.get("name", "").strip()
        applicant_email = request.POST.get("email", "").strip()
        applicant_phone = request.POST.get("phone", "").strip()
        location = request.POST.get("location", "").strip()
        message = request.POST.get("message", "").strip()


        required_fields = {
            "Name": applicant_name,
            "Email": applicant_email,
            "Phone": applicant_phone,
            "location": location,
            "message": message
        }

        for field_name, field_value in required_fields.items():
            if not field_value:
                messages.warning(request, f"{field_name} is required")
                return redirect(self.get_redirect_url())

        ServiceEnquiry.objects.create(
            applicant_name=applicant_name, applicant_email=applicant_email,
            applicant_phone=applicant_phone, location=location, message=message,
            service = service
            )
        messages.success(request, "Service Enquiry submitted successfully")
        return redirect(self.get_success_url())


