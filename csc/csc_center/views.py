from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import CscCenter

class CreateCscCenterView(CreateView):
    model = CscCenter
    template_name = 'csc_center/add.html'
    success_url = reverse_lazy('csc_center:create')
    fields = "__all__"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "CSC center creation successfull.")
        return response
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field - {field}: {error}")

        return super().form_valid(form)