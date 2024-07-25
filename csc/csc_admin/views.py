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
from django.utils import timezone
from datetime import datetime
import re
import os
from django.conf import settings

from .forms import (
    CreateServiceForm, UpdateServiceForm, CreateBlogForm,
    UpdateBlogForm
    )

from products.models import Product, Category as ProductCategory
from csc_center.models import CscCenter, State, District, Block, CscKeyword, CscNameType, SocialMediaLink, Image
from services.models import Service
from blog.models import Blog, Category, Tag

class BaseAdminView(LoginRequiredMixin, View):
    login_url = reverse_lazy("authentication:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
        
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


@method_decorator(never_cache, name="dispatch")
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

@method_decorator(never_cache, name="dispatch")
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
    redirect_url = success_url
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

        if Blog.objects.filter(title = title).exists():
            messages.error(request, 'Blog with this title already exists. Please try again with another title')            
            return redirect(self.redirect_url)
        
        try:
            form = self.get_form()
            if form.is_valid():
                content = form.cleaned_data['content']
                blog = Blog.objects.create(
                    title = title, image = image, author = author,
                    summary = summary, content = content
                    )
                
                if category_list:
                    blog.categories.set(category_list)
                    blog.save()
                
                if tags:
                    tag_list = tags.split(',')
                    for tag in tag_list:
                        tag = tag.strip().title()
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
                return redirect(self.redirect_url)
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
                        tag = tag.strip().title()
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
            self.object = get_object_or_404(Blog, slug = self.kwargs['slug'])
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
    
    

@method_decorator(csrf_exempt, name="dispatch")
class ChangeBlogStatusView(BaseAdminBlogView, UpdateView):        

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status == "Published":
            self.object.status = "Draft"
            self.object.published_at = None
        elif self.object.status == "Draft":
            self.object.status = "Published"
            self.object.published_at = timezone.now()
        self.object.save()
        return JsonResponse({"message": "Successfully published blog.", "status": self.object.status})
##################################### BLOG END #####################################

##################################### PRODUCT START #####################################

@method_decorator(never_cache, name="dispatch")
class BaseAdminCscProductView(BaseAdminView, View):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_categories'] = ProductCategory.objects.all().order_by('name')        
        return context
    

class CreateProductView(BaseAdminCscProductView, CreateView):
    fields = ["image", "name", "description", "price", "category"]
    template_name = "admin_product/create.html"
    success_url = reverse_lazy("csc_admin:create_product")

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        category = request.POST.get('category')

        try:
            category = get_object_or_404(ProductCategory, slug = category)
        except Http404:
            messages.error(self.request, "Failed. Invalid category")
            return redirect('csc_admin:create_product')
        
        self.model.objects.create(name = name, image = image, description = description, price = price, quantity = quantity, category = category)
        messages.success(self.request, "Created Product")
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        response = super().form_invalid(form)
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field '{field}': {error}")                
        return response
    

class ProductListView(BaseAdminCscProductView, ListView):
    template_name = "admin_product/list.html"
    context_object_name = "products"


class ProductDetailView(BaseAdminCscProductView, DetailView):
    template_name = "admin_product/detail.html"
    context_object_name = "product"


class UpdateProductView(BaseAdminCscProductView, UpdateView):
    fields = ["image", "name", "description", "price", "category", "quantity"]
    template_name = "admin_product/update.html"
    
    def get_success_url(self, *kwargs):
        return reverse_lazy("csc_admin:product", kwargs = {"slug" : self.object.slug})
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        image = request.FILES.get('image')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        category = request.POST.get('category')

        try:
            category = get_object_or_404(ProductCategory, slug = category)
        except Http404:
            messages.error(self.request, "Failed. Invalid category")
            return redirect('csc_admin:create_product')
        
        self.object = self.get_object()
        if not image:
            image = self.object.image
        
        self.object.name = name
        self.object.image = image
        self.object.description = description
        self.object.price = price
        self.object.quantity = quantity
        self.object.category = category
        self.object.save()

        messages.success(self.request, "Updated Product")
        return redirect(self.get_success_url())

    def form_invalid(self, form):        
        response = super().form_invalid(form)        

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field '{field}': {error}")
        return response
    

class DeleteProductView(BaseAdminCscProductView, View):
    success_url = reverse_lazy('csc_admin:products')

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = kwargs['slug'])
        except Http404:
            messages.error(request, 'Invalid Product')
            return redirect(reverse_lazy('csc_admin:products'))
        self.object.delete()
        messages.success(self.request, "Deleted Product")
        return redirect(self.success_url)

##################################### PRODUCT END #####################################

##################################### CSC CENTER START #####################################

@method_decorator(never_cache, name="dispatch")
class BaseAdminCscCenterView(BaseAdminView, View):
    model = CscCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csc_center_page'] = True
        context.update({
            'states': State.objects.all().order_by('state'),
            'districts': District.objects.all().order_by('district'),
            'blocks': Block.objects.all().order_by('block'),
            })
        return context


class ListCscCenterView(BaseAdminCscCenterView, ListView):
    template_name = "admin_csc_center/list.html"
    paginate_by = 10
    paginate_orphans = 5
    ordering = ['name']
    context_object_name = 'centers'
    queryset = CscCenter.objects.all().order_by('name')


class AddCscCenterView(BaseAdminCscCenterView, CreateView):
    template_name = 'admin_csc_center/create.html'
    success_url = reverse_lazy('csc_admin:add_csc')
    fields = "__all__"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_types'] = CscNameType.objects.all().order_by('type')
        context['keywords'] = CscKeyword.objects.all().order_by('keyword')
        context['products'] = Product.objects.all()
        context['states'] = State.objects.all()

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
        contact_number = request.POST.get('contact_number')
        mobile_number = request.POST.get('mobile_number')
        whatsapp_number = request.POST.get('whatsapp_number')
        email = request.POST.get('email')
        website = request.POST.get('website') # optional
        services = request.POST.getlist('services')
        products = request.POST.getlist('products')

        mon_opening_time = request.POST.get('mon_opening_time') #timefield
        tue_opening_time = request.POST.get('tue_opening_time') #timefield
        wed_opening_time = request.POST.get('wed_opening_time') #timefield
        thu_opening_time = request.POST.get('thu_opening_time') #timefield
        fri_opening_time = request.POST.get('fri_opening_time') #timefield
        sat_opening_time = request.POST.get('sat_opening_time') #timefield
        sun_opening_time = request.POST.get('sun_opening_time') #timefield

        mon_closing_time = request.POST.get('mon_closing_time') #timefield
        tue_closing_time = request.POST.get('tue_closing_time') #timefield
        wed_closing_time = request.POST.get('wed_closing_time') #timefield
        thu_closing_time = request.POST.get('thu_closing_time') #timefield
        fri_closing_time = request.POST.get('fri_closing_time') #timefield
        sat_closing_time = request.POST.get('sat_closing_time') #timefield
        sun_closing_time = request.POST.get('sun_closing_time') #timefield

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

        social_medias = request.POST.getlist('social_media') # manytomany
        social_links = request.POST.getlist('social_links') # manytomany

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        try:
            type = get_object_or_404(CscNameType, slug = type)
        except Http404:
            messages.error(request, 'Invalid CSC Name Type')
            return redirect(reverse_lazy('csc_admin:add_csc'))

        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            messages.error(request, 'Invalid State')
            return redirect(reverse_lazy('csc_admin:add_csc'))

        try:
            district = get_object_or_404(District, pk = district)
        except Http404:
            messages.error(request, 'Invalid District')
            return redirect(reverse_lazy('csc_admin:add_csc'))
        
        try:
            block = get_object_or_404(Block, pk = block)
        except Http404:
            messages.error(request, 'Invalid Block')
            return redirect(reverse_lazy('csc_admin:add_csc'))
        
        self.object = CscCenter.objects.create(
            name = name, type = type, state = state,
            district = district,block = block,location = location,
            zipcode = zipcode, landmark_or_building_name = landmark_or_building_name,
            street = street, logo = logo, banner = banner,
            description = description, contact_number = contact_number,
            mobile_number = mobile_number, whatsapp_number = whatsapp_number,
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

        messages.success(request, "Added CSC center")      
        
        # after creation of object
        self.object.keywords.set(keywords)
        self.object.services.set(services)
        self.object.products.set(products)
        self.object.save()

        social_media_length = len(social_medias)
        if social_media_length > 0:
            social_media_list = []
            for i in range(social_media_length):
                social_media_link, created = SocialMediaLink.objects.get_or_create(
                    csc_center_id = self.object,
                    social_media_name = social_medias[i],
                    social_media_link = social_links[i]
                )
                social_media_list.append(social_media_link)
            
            self.object.social_media_links.set(social_media_list)
            self.object.save()
        
        return redirect(self.success_url)

class DetailCscCenterView(BaseAdminCscCenterView, DetailView):
    template_name = "admin_csc_center/detail.html"
    context_object_name = 'center'


@method_decorator(never_cache, name="dispatch")
class UpdateCscCenterView(BaseAdminCscCenterView, UpdateView):
    template_name = 'admin_csc_center/update.html'
    context_object_name = 'center'
    fields = "__all__"
    pk_url_kwarg = 'slug'

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(self.model, slug = self.kwargs['slug'])
        except Http404:
            messages.error(self.request, "Invalid CSC center")
            return redirect(reverse_lazy('csc_admin:csc_centers'))
        
    def get_success_url(self):
        return reverse_lazy('csc_admin:csc_center', kwargs = {'slug': self.kwargs.get('slug')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name_types'] = CscNameType.objects.all().order_by('type')
        context['keywords'] = CscKeyword.objects.all().order_by('keyword')
        context['products'] = Product.objects.all()
        context['states'] = State.objects.all()
        context['social_medias'] = ["Facebook", "Instagram", "Twitter", "YouTube", "LinkedIn", "Pinterest", "Tumblr"]
        self.object = self.get_object()
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
        contact_number = request.POST.get('contact_number')
        mobile_number = request.POST.get('mobile_number')
        whatsapp_number = request.POST.get('whatsapp_number')
        email = request.POST.get('email')
        website = request.POST.get('website') # optional
        services = request.POST.getlist('services')
        products = request.POST.getlist('products')

        mon_opening_time = request.POST.get('mon_opening_time') #timefield
        tue_opening_time = request.POST.get('tue_opening_time') #timefield
        wed_opening_time = request.POST.get('wed_opening_time') #timefield
        thu_opening_time = request.POST.get('thu_opening_time') #timefield
        fri_opening_time = request.POST.get('fri_opening_time') #timefield
        sat_opening_time = request.POST.get('sat_opening_time') #timefield
        sun_opening_time = request.POST.get('sun_opening_time') #timefield

        mon_closing_time = request.POST.get('mon_closing_time') #timefield
        tue_closing_time = request.POST.get('tue_closing_time') #timefield
        wed_closing_time = request.POST.get('wed_closing_time') #timefield
        thu_closing_time = request.POST.get('thu_closing_time') #timefield
        fri_closing_time = request.POST.get('fri_closing_time') #timefield
        sat_closing_time = request.POST.get('sat_closing_time') #timefield
        sun_closing_time = request.POST.get('sun_closing_time') #timefield

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

        social_medias = request.POST.getlist('social_media') # manytomany
        social_links = request.POST.getlist('social_links') # manytomany

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        try:
            type = get_object_or_404(CscNameType, slug = type)
        except Http404:
            messages.error(request, 'Invalid CSC Name Type')
            return redirect(reverse_lazy('csc_admin:add_csc'))

        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            messages.error(request, 'Invalid State')
            return redirect(reverse_lazy('csc_admin:add_csc'))

        try:
            district = get_object_or_404(District, pk = district)
        except Http404:
            messages.error(request, 'Invalid District')
            return redirect(reverse_lazy('csc_admin:add_csc'))
        
        try:
            block = get_object_or_404(Block, pk = block)
        except Http404:
            messages.error(request, 'Invalid Block')
            return redirect(reverse_lazy('csc_admin:add_csc'))
        
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
        self.object.contact_number = contact_number
        self.object.mobile_number = mobile_number
        self.object.whatsapp_number = whatsapp_number
        self.object.email = email
        self.object.website = website

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

        social_media_length = len(social_medias)
        if social_media_length > 0:
            social_media_list = []
            for i in range(social_media_length):
                social_media_link, created = SocialMediaLink.objects.get_or_create(
                    csc_center_id = self.object,
                    social_media_name = social_medias[i],
                    social_media_link = social_links[i]
                )
                social_media_list.append(social_media_link)
            
            self.object.social_media_links.set(social_media_list)
            self.object.save()

        messages.success(request, "Updated CSC Center Details")      
        
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field - {field}: {error}")
        return super().form_invalid(form)


class DeleteCscCenterView(BaseAdminCscCenterView, View):
    success_url = reverse_lazy('csc_admin:csc_centers')
    redirect_url = success_url

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscCenter, slug = kwargs['slug'])
        except Http404:
            messages.error(request, 'Invalid CSC Center')
            return redirect(self.redirect_url)
        
        self.object.delete()
        messages.success(request, "Deleted CSC Center")
        return redirect(self.success_url)


@method_decorator(csrf_exempt, name="dispatch")
class RemoveCscCenterLogoView(BaseAdminCscCenterView, UpdateView):
    fields = ["logo"]
    pk_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.logo = None
        self.object.save()
        return JsonResponse({'message': 'success'})

    
@method_decorator(csrf_exempt, name="dispatch")
class RemoveCscCenterBannerView(BaseAdminCscCenterView, UpdateView):
    fields = ["banner"]
    pk_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.banner = None
        self.object.save()
        return JsonResponse({'message': 'success'})


# Nuclear
class GetDistrictView(View):
    def get(self, request, *args, **kwargs):
        state_id = request.GET.get('state_id')
        districts = list(District.objects.filter(state__pk=state_id).values())
        return JsonResponse({"districts": districts}, safe=False)
    

class GetBlockView(View):
    def get(self, request, *args, **kwargs):
        district_id = request.GET.get('district_id')
        state_id = request.GET.get('state_id')
        blocks = list(Block.objects.filter(district__id = district_id, state__id = state_id).values())
        return JsonResponse({"blocks": blocks}, safe=False)
    

# Json
def get_all_states(request):
    states = list(State.objects.all().order_by('state').values())
    return JsonResponse({"states": states}, safe=False)

def get_all_districts(request):
    districts = list(District.objects.all().order_by('district').values())
    return JsonResponse({"districts": districts}, safe=False)

def get_all_blocks(request):
    blocks = list(Block.objects.all().order_by('block').values())
    return JsonResponse({"blocks": blocks}, safe=False)

def get_name_types(request):
    name_types = list(CscNameType.objects.all().order_by('type').values())
    return JsonResponse({"name_types": name_types}, safe=False)

def get_csc_keywords(request):
    keywords = list(CscKeyword.objects.all().order_by('keyword').values())
    return JsonResponse({"keywords": keywords}, safe=False)

class GetDistrictDetailsView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            district = get_object_or_404(District, pk = self.kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "District not found"}, safe=False)
        
        return JsonResponse({"district": district.district, "state": district.state.state, "state_id": district.state.pk})
    

class GetBlockDetailsView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            block = get_object_or_404(Block, pk = self.kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "Block not found"}, safe=False)
        
        return JsonResponse({
            "block": block.block,
            "state": block.state.state,
            "state_id": block.state.pk,
            "district": block.district.district,
            "district_id": block.district.pk
            })

# Geographic Views
@method_decorator(csrf_exempt, name="dispatch")
class CreateStateView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        state = request.POST.get('state').title()

        if not state:
            return JsonResponse({"error": "State is required"}, status=400)
        
        if not State.objects.filter(state = state).exists():
            State.objects.create(state = state)
            return JsonResponse({"status": "success"}, safe=False)
        else:
            return JsonResponse({"error": "State already exists"}, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class EditStateView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(State, pk = self.kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "State does not exist"}, status=400)
        
        state = request.POST.get('state').title()

        if not state:
            return JsonResponse({"error": "State is required"}, status=400)        

        existing_state = State.objects.filter(state = state)
        if not existing_state.exists() or existing_state.first().pk == self.object.pk:        
            self.object.state = state
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)
        else:
            return JsonResponse({"error": "State already exists"}, safe=False)


class DeleteStateView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(State, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "Block does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)    


@method_decorator(csrf_exempt, name="dispatch")
class CreateDistrictView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        state = request.POST.get('state')
        districts = request.POST.get('districts')
        
        if not state:
            return JsonResponse({"error": "State is required"}, safe=False)
        
        try:
            state = State.objects.get(pk = state)
        except Http404:
            return JsonResponse({"error": "State does not exist"}, safe=False)
        
        if not districts:
            return JsonResponse({"error": "District is required"}, safe=False)

        district_list = districts.split(",")        
        filtered_district_list = []
        for district in district_list:
            if re.match(r'^[a-zA-Z0-9 ]+$', district) and district.strip():
                filtered_district_list.append(district)

        filtered_list_length = len(filtered_district_list)

        created_count = 0
        for district in filtered_district_list:
            district = district.strip().title()
            if not District.objects.filter(state = state, district = district).exists():
                District.objects.create(state = state, district = district)
                created_count += 1

        if created_count > 0:
            return JsonResponse({"status": "success"}, safe=False)
        else:
            if filtered_list_length > 1:
                return JsonResponse({"error": f"Districts already exists for the state '{state}'"}, safe=False)
            else:
                return JsonResponse({"error": f"District already exists for the state '{state}'"}, safe=False)
            

@method_decorator(csrf_exempt, name="dispatch")
class EditDistrictView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(District, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "District does not exist"}, safe=False)

        state = request.POST.get('state')
        district = request.POST.get('district').title().strip()
        
        if not state:
            return JsonResponse({"error": "State is required"}, safe=False)
        
        if not district:
            return JsonResponse({"error": "District is required"}, safe=False)
        
        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            return JsonResponse({"error": "State does not exist"}, safe=False)        
        
        existing_district = District.objects.filter(state = state, district = district)
        if not existing_district.exists() or existing_district.first().pk == self.object.pk:            
            self.object.state = state
            self.object.district = district
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)        
        else:            
            return JsonResponse({"error": f"District already exists for the state '{state}'"}, safe=False)
        

class DeleteDistrictView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(District, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "District does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class CreateBlockView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        state = request.POST.get('state')
        district = request.POST.get('district')
        blocks = request.POST.get('blocks')
        
        if not state:
            return JsonResponse({"error": "State is required"}, safe=False)
        
        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            return JsonResponse({"error": "State does not exist"}, safe=False)
        
        if not district:
            return JsonResponse({"error": "District is required"}, safe=False)
        
        try:
            district = get_object_or_404(District, pk = district)
        except Http404:
            return JsonResponse({"error": "District does not exist"}, safe=False)

        if not blocks:
            return JsonResponse({"error": "Block is required"}, safe=False)

        block_list = blocks.split(",")        
        filtered_block_list = []
        for block in block_list:
            if re.match(r'^[a-zA-Z0-9 ]+$', block) and block.strip():
                filtered_block_list.append(block)

        filtered_list_length = len(filtered_block_list)

        created_count = 0
        for block in filtered_block_list:
            block = block.strip().title()
            if not Block.objects.filter(state = state, district = district, block = block).exists():
                Block.objects.create(state = state, district = district, block = block)
                created_count += 1

        if created_count > 0:
            return JsonResponse({"status": "success"}, safe=False)
        else:
            if filtered_list_length > 1:
                return JsonResponse({"error": f"Blocks already exists for the district '{district}' of state '{state}'"}, safe=False)
            else:
                return JsonResponse({"error": f"Block already exists for the district '{district}' of state '{state}'"}, safe=False)
            

@method_decorator(csrf_exempt, name="dispatch")
class EditBlockView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Block, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "Block does not exist"}, safe=False)

        state = request.POST.get('state')
        district = request.POST.get('district')
        block = request.POST.get('block').title().strip()
        
        if not state:
            return JsonResponse({"error": "State is required"}, safe=False)
        
        if not district:
            return JsonResponse({"error": "District is required"}, safe=False)
        
        if not block:
            return JsonResponse({"error": "Block is required"}, safe=False)
        
        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            return JsonResponse({"error": "State does not exist"}, safe=False)

        try:
            district = get_object_or_404(District, pk = district)
        except Http404:
            return JsonResponse({"error": "District does not exist"}, safe=False)

        existing_block = Block.objects.filter(state = state, district = district, block = block)
        if not existing_block.exists() or existing_block.first().pk == self.object.pk:    
            self.object.state = state
            self.object.district = district
            self.object.block = block
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)

        else:            
            return JsonResponse({"error": f"Block already exists for the district '{district}' of state '{state}'"}, safe=False)
        

class DeleteBlockView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Block, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "Block does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)
    

# CSC modules
@method_decorator(csrf_exempt, name="dispatch")
class CreateKeywordView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        keyword = request.POST.get('keyword')

        if not keyword:
            return JsonResponse({"error": "Keyword is required"}, status=400)
        
        if not CscKeyword.objects.filter(keyword = keyword).exists():
            CscKeyword.objects.create(keyword = keyword)
            return JsonResponse({"status": "success"}, safe=False)
        else:
            return JsonResponse({"error": "Keyword already exists"}, safe=False)
        

@method_decorator(csrf_exempt, name="dispatch")
class EditKeywordView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscKeyword, slug = self.kwargs['slug'])
        except Http404:
            return JsonResponse({"error": "Keyword does not exist"}, status=400)
        
        keyword = request.POST.get('keyword')

        if not keyword:
            return JsonResponse({"error": "Keyword is required"}, status=400)        

        existing_keyword = CscKeyword.objects.filter(keyword = keyword)
        if not existing_keyword.exists() or existing_keyword.first().slug == self.object.slug:
            self.object.keyword = keyword
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)
        else:
            return JsonResponse({"error": "Keyword already exists"}, safe=False)


class DeleteKeywordView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscKeyword, slug = kwargs['slug'])
        except Http404:
            return JsonResponse({"error": "Keyword does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)
    

@method_decorator(csrf_exempt, name="dispatch")
class CreateCscNameTypeView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        name_type = request.POST.get('name_type')

        if not name_type:
            return JsonResponse({"error": "Name Type is required"}, status=400)
        
        if not CscNameType.objects.filter(type = name_type).exists():
            CscNameType.objects.create(type = name_type)
            return JsonResponse({"status": "success"}, safe=False)
        else:
            return JsonResponse({"error": "Name Type already exists"}, safe=False)
        

@method_decorator(csrf_exempt, name="dispatch")
class EditCscNameTypeView(BaseAdminCscCenterView, View):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscNameType, slug = self.kwargs['slug'])
        except Http404:
            return JsonResponse({"error": "Name Type does not exist"}, status=400)
        
        name_type = request.POST.get('name_type')

        if not name_type:
            return JsonResponse({"error": "Name Type is required"}, status=400)        

        existing_name_type = CscNameType.objects.filter(type = name_type)
        if not existing_name_type.exists() or existing_name_type.first().slug == self.object.slug:
            self.object.type = name_type
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)
        else:
            return JsonResponse({"error": "Name type already exists"}, safe=False)
        

class DeleteCscNameTypeView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(CscNameType, slug = kwargs['slug'])
        except Http404:
            return JsonResponse({"error": "Name type does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)
##################################### CSC CENTER END #####################################