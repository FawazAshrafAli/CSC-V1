from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, CreateView, DetailView, UpdateView, ListView
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from .forms import CreateServiceForm, UpdateServiceForm

from services.models import Service

class BaseAdminView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().get(request, *args, **kwargs)


class AdminHomeView(BaseAdminView, TemplateView):
    template_name = 'admin_home/home.html'


@method_decorator(csrf_exempt, name="dispatch")
class CreateServiceView(BaseAdminView, CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'admin_service/create.html'
    success_url = reverse_lazy('csc_admin:create_service')
    
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        name = request.POST.get('name')
        image = request.FILES.get('image')

        if name:
            self.service = self.model.objects.create(name = name, image = image)
            if form.is_valid():
                description = form.cleaned_data['description']
                self.service.description = description
                self.service.save()

            print("Created")
            messages.success(request, 'Successfully created new service.')
            return redirect(self.success_url)
        else:
            messages.warning(request, 'Please provide the service name.')
            return redirect(reverse_lazy('csc_admin:create_service'))
        
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.model.objects.all().last()
        context['service'] = service
        return context
                                    


class UpdateServiceView(BaseAdminView, UpdateView):
    model = Service
    form_class = UpdateServiceForm
    template_name = 'admin_service/update.html'
    context_object_name = "service"

    def get_success_url(self, **kwargs):
        return reverse_lazy('csc_admin:service', kwargs = {'pk' : self.kwargs['pk']})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        name = request.POST.get('name')
        image = request.FILES.get('image')

        if name:
            if form.is_valid():
                form.save(commit=False)
                self.object.name = name                
                self.object.image = image if image else self.object.image
                self.object.save()

                messages.success(request, "Service details successfully updated.")        
                return redirect(self.get_success_url())
            else:
                messages.error(request, "Error in updation details of service.")
                return self.form_invalid(form)
        else:
            messages.error(request, "Please Provide a service name")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Erron on field - {field}: {error}")
        reverse_lazy('csc_admin:service', kwargs = {'pk' : self.kwargs['pk']})


# @method_decorator(never_cache, name="dispatch")
class ListServiceView(BaseAdminView, ListView):
    model = Service
    queryset = Service.objects.all()
    template_name = 'admin_service/list.html'
    context_object_name = "services"



# Nuclear Views
@method_decorator(csrf_exempt, name="dispatch")
class RemoveServiceImageView(BaseAdminView, UpdateView):
    model = Service
    field = ['image']
    

    def get_success_url(self, **kwargs):
        return reverse_lazy('csc_admin:update_service', kwargs = {'pk' : self.kwargs['pk']})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.image = None
        self.object.save()
        return JsonResponse({"message": "Successfully removed image."})



@method_decorator(never_cache, name="dispatch")
class DetailServiceView(BaseAdminView, DetailView):
    model = Service
    template_name = 'admin_service/detail.html'
    context_object_name = "service"
    form_class = UpdateServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context


class JsonSeviceDetailView(BaseAdminView, DetailView):
    model = Service

    def render_to_response(self, context):
        service = context['object']
        name = service.name
        return JsonResponse({'name': name})
    

@method_decorator(never_cache, name="dispatch")
class DeleteServiceView(BaseAdminView, View):
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