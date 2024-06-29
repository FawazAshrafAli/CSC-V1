from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, CreateView, DetailView, UpdateView, ListView
from django.http import JsonResponse, Http404
from django.contrib import messages

from .forms import CreateServiceForm, UpdateServiceForm

from services.models import Service

class AdminHomeView(TemplateView):
    template_name = 'admin_home/home.html'



class CreateServiceView(CreateView):
    model = Service
    template_name = 'admin_service/create.html'
    success_url = reverse_lazy('csc_admin:services')
    fields = ["name", "image", "description"]


class UpdateServiceView(UpdateView):
    model = Service
    form_class = UpdateServiceForm
    template_name = 'admin_service/detail.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('csc_admin:service', kwargs = {'pk' : self.kwargs['pk']})

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erron on field - {field}: {error}")
        return super().form_invalid(form)


@method_decorator(never_cache, name="dispatch")
class ListServiceView(ListView):
    model = Service
    queryset = Service.objects.all()
    template_name = 'admin_service/list.html'
    context_object_name = "services"
    form_class = CreateServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        return context


@method_decorator(never_cache, name="dispatch")
class DetailServiceView(DetailView):
    model = Service
    template_name = 'admin_service/detail.html'
    context_object_name = "service"
    form_class = UpdateServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context


class JsonSeviceDetailView(DetailView):
    model = Service

    def render_to_response(self, context):
        service = context['object']
        name = service.name
        return JsonResponse({'name': name})
    

@method_decorator(never_cache, name="dispatch")
class DeleteServiceView(View):
    model = Service
    success_url = reverse_lazy('csc_admin:services')

    def get(self, request, *args, **kwargs):
        try:
            try:
                self.object = get_object_or_404(Service, pk = self.kwargs['pk'])
                self.object.delete()
                messages.success(self.request, "Successfully deleted service.")
                return redirect(self.success_url)
            except Http404:            
                pass
        except Exception as e:
            print(e)
            pass