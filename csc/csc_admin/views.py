from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, CreateView, DetailView, UpdateView, ListView
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from .forms import (
    CreateServiceForm, UpdateServiceForm, CreateBlogForm,
    UpdateBlogForm
    )

from services.models import Service
from blog.models import Blog, Category, Tag

class BaseAdminView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:            
            return super().get(request, *args, **kwargs)
        else:
             return redirect(reverse_lazy('authentication:login'))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        return context
    


class AdminHomeView(BaseAdminView, TemplateView):
    template_name = 'admin_home/home.html'


##################################### SERVICE START #####################################
@method_decorator(csrf_exempt, name="dispatch")
class CreateServiceView(BaseAdminView, CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'admin_service/create.html'
    success_url = reverse_lazy('csc_admin:create_service')
    
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
        context['form'] = self.get_form()
        context['service_page'] = True
        return context
                                    


class UpdateServiceView(BaseAdminView, UpdateView):
    model = Service
    form_class = UpdateServiceForm
    template_name = 'admin_service/update.html'
    context_object_name = "service"

    def get_success_url(self, **kwargs):
        return reverse_lazy('csc_admin:service', kwargs = {'pk' : self.kwargs['pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context
    
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context
    

@method_decorator(never_cache, name="dispatch")
class DetailServiceView(BaseAdminView, DetailView):
    model = Service
    template_name = 'admin_service/detail.html'
    context_object_name = "service"
    form_class = UpdateServiceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        context['service_page'] = True
        return context
    

@method_decorator(never_cache, name="dispatch")
class DeleteServiceView(BaseAdminView, View):
    model = Service
    success_url = reverse_lazy('csc_admin:services')

    def get(self, request, *args, **kwargs):
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


# Nuclear Views
@method_decorator(csrf_exempt, name="dispatch")
class RemoveServiceImageView(BaseAdminView, UpdateView):
    model = Service
    field = ['image']    
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.image = None
        self.object.save()
        return JsonResponse({"message": "Successfully removed image."})

##################################### SERVICE END #####################################


##################################### BLOG START #####################################

class BaseAdminBlogView(BaseAdminView, View):
    model = Blog

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blog_page'] = True
        return context

class BlogListView(BaseAdminBlogView, ListView):
    template_name = 'admin_blog/list.html'
    queryset = Blog.objects.all()
    context_object_name = 'blogs'


class BlogDetailView(BaseAdminBlogView, DetailView):
    template_name = 'admin_blog/detail.html'
    query_pk_and_slug = 'slug'


class CreateBlogView(BaseAdminBlogView, CreateView):
    template_name = 'admin_blog/create.html'
    success_url = reverse_lazy('csc_admin:create_blog')
    redirection_url = success_url
    form_class = CreateBlogForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['categories'] = Category.objects.all().order_by('name')
        return context    

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')        
        image = request.FILES.get('image')        
        category_list = request.POST.getlist('category')
        summary = request.POST.get('summary')        
        author = request.user
        tags = request.POST.get('tags')
        
        try:
            form = self.get_form()
            if form.is_valid():
                content = form.cleaned_data['content']
                blog = Blog.objects.create(
                    title = title, image = image, author = author,
                    summary = summary, content = content                    )
                
                if category_list:
                    blog.categories.set(category_list)
                    blog.save()
                
                if tags:
                    tag_list = tags.split(',')
                    for tag in tag_list:
                        tag = tag.strip().capitalize()
                        if tag not in (' ', ','):
                            tag_obj = Tag.objects.filter(name = tag)                                                        
                            if not tag_obj.exists():
                                tag_obj = Tag.objects.create(name = tag)
                            else:
                                tag_obj = tag_obj.first().pk
                            blog.tags.add(tag_obj)
                            blog.save()                                    

                messages.success(request, "Blog Saved")
                return redirect(self.success_url)
            else:
                messages.error(request, "Content cannot be empty.")
                return redirect(self.redirection_url)
        except Exception as e:
            print(e)
            return HttpResponse(f"Error 404: {e}")


class UpdateBlogView(BaseAdminBlogView, UpdateView):
    template_name = 'admin_blog/update.html'
    form_class = UpdateBlogForm
    pk_url_kwarg = 'slug'

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(Blog, slug = self.kwargs[self.pk_url_kwarg])
        except Http404:
            pass

    def get_success_url(self):
        return reverse_lazy('csc_admin:blog', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['categories'] = Category.objects.all().order_by('name')
        return context    

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')        
        image = request.FILES.get('image')        
        category_list = request.POST.getlist('category')
        summary = request.POST.get('summary')        
        author = request.user
        tags = request.POST.get('tags')
        
        try:
            form = self.get_form()
            if form.is_valid():
                content = form.cleaned_data['content']
                self.object = self.get_object()
                self.object.title = title
                self.object.summary = summary
                self.object.author = author
                self.object.content = content
                if image:
                    self.object.image = image
                self.object.save()

                if category_list:
                    self.object.categories.set(category_list)
                    self.object.save()
                
                if tags:
                    tag_list = tags.split(',')
                    for tag in tag_list:
                        tag = tag.strip().capitalize()
                        if tag not in (' ', ',', ''):
                            tag_obj = Tag.objects.filter(name = tag)                                                        
                            if not tag_obj.exists():
                                tag_obj = Tag.objects.create(name = tag)
                            else:
                                tag_obj = tag_obj.first().pk                                
                            self.object.tags.add(tag_obj)
                            self.object.save()                                    

                messages.success(request, "Blog Saved")
                return redirect(self.get_success_url())
            else:
                messages.error(request, "Content field cannot be empty.")
                self.redirect_url = self.success_url
                return redirect(self.redirect_url)
        except Exception as e:
            print(e)
            return HttpResponse(f"Error 404: {e}")


class DeleteBlogView(BaseAdminBlogView, View):
    success_url = reverse_lazy('csc_admin:blogs')

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Blog, pk = self.kwargs['pk'])
            self.object.delete()
            messages.success(self.request, "Successfully deleted blog.")
            return redirect(self.success_url)
        
        except Http404:            
            pass
        except Exception as e:
            print(e)
            pass


# Nuclear
@method_decorator(csrf_exempt, name="dispatch")
class RemoveBlogImageView(BaseAdminBlogView, UpdateView):
    field = ['image']    
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.image = None
        self.object.save()
        return JsonResponse({"message": "Successfully removed image."})
##################################### BLOG END #####################################