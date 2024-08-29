from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Enquiry

class ContactUsView(TemplateView):
    template_name = "contact_us/contact_us.html"


class SubmitEnquiryView(ContactUsView, CreateView):
    model = Enquiry
    fields = ["name", "email", "subject", "message"]
    success_url = reverse_lazy("contact_us:view")
    redirect_url = success_url

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Enquiry Submitted")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "Enquiry Submission Failed")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field - {field}: {error}")
        return super().form_invalid(form)
