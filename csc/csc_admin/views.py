from django.db.models.query import QuerySet
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
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
from django.contrib.auth import authenticate, logout
from django.core.mail import send_mail
import re

from contact_us.models import Enquiry
from faq.models import Faq
from authentication.models import User
from .forms import (
    CreateServiceForm, UpdateServiceForm, CreateBlogForm,
    UpdateBlogForm
    )

from products.models import Product, Category as ProductCategory, ProductEnquiry
from csc_center.models import CscCenter, State, District, Block, CscKeyword, CscNameType, SocialMediaLink, Banner
from services.models import Service, ServiceEnquiry
from blog.models import Blog, Category, Tag
from posters.models import Poster
from .models import CscCenterAction, ServiceEnquiry as AdminServiceEnquiry, ProductEnquiry as AdminProductEnquiry
from payment.models import Payment, Price

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_confirm_creation(center, payment_link):
    subject = 'Welcome to Our Website'
    from_email = 'w3digitalpmna@gmail.com'
    to_email = [center.email]
    
    html_content = render_to_string('admin_email_templates/csc_approve.html', {'name': center.name, 'owner': center.owner if center.owner else center.email, 'payment_link': payment_link})
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()

class BaseAdminView(LoginRequiredMixin):
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

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['csc_centers'] = CscCenter.objects.all()
        context['services'] = Service.objects.all()
        context['products'] = Product.objects.all()
        context['posters'] = Poster.objects.all()
        context['home_page'] = True
        return context


##################################### SERVICE START #####################################
# @method_decorator(csrf_exempt, name="dispatch")
class AdminBaseServiceView(BaseAdminView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_page'] = True
        return context


class CreateServiceView(AdminBaseServiceView, CreateView):
    model = Service
    form_class = CreateServiceForm
    template_name = 'admin_service/create.html'
    success_url = reverse_lazy('csc_admin:create_service')
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        name = request.POST.get('name').strip()
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
        return context
                                    

class UpdateServiceView(AdminBaseServiceView, UpdateView):
    model = Service
    form_class = UpdateServiceForm
    template_name = 'admin_service/update.html'
    context_object_name = "service"

    def get_success_url(self, **kwargs):
        return reverse_lazy('csc_admin:service', kwargs = {'pk' : self.kwargs['pk']})
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        name = request.POST.get('name').strip()
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
class ListServiceView(AdminBaseServiceView, ListView):
    model = Service
    queryset = Service.objects.all()
    template_name = 'admin_service/list.html'
    context_object_name = "services"
    

@method_decorator(never_cache, name="dispatch")
class DetailServiceView(AdminBaseServiceView, DetailView):
    model = Service
    template_name = 'admin_service/detail.html'
    context_object_name = "service"
    form_class = UpdateServiceForm
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context
    

@method_decorator(never_cache, name="dispatch")
class DeleteServiceView(AdminBaseServiceView, View):
    model = Service
    success_url = reverse_lazy('csc_admin:services')

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Service, slug = self.kwargs['slug'])
            self.object.delete()
            messages.success(self.request, "Successfully deleted service.")
            return redirect(self.success_url)
        
        except Http404:            
            pass
        except Exception as e:
            print(e)
            pass


class ServiceEnquiryListView(AdminBaseServiceView, ListView):
    model = AdminServiceEnquiry
    queryset = model.objects.all().order_by('-created')
    context_object_name = "enquiries"
    template_name = "admin_service/enquiry_list.html"


class DeleteServiceEnquiryView(AdminBaseServiceView, View):
    model = AdminServiceEnquiry
    success_url = redirect_url = reverse_lazy("csc_admin:service_enquiries")

    def get_object(self):
        try:
            return get_object_or_404(AdminServiceEnquiry, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Service Enquiry")
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()        
            self.object.delete()
            messages.success(self.request, "Successfully deleted service enquiry.")
            return redirect(self.success_url)
        except Exception as e:
            print(f"Error: {e}")
            return redirect(self.redirect_url)


# Nuclear Views
@method_decorator(csrf_exempt, name="dispatch")
class RemoveServiceImageView(AdminBaseServiceView, UpdateView):
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
        title = request.POST.get('title').strip()
        image = request.FILES.get('image')        
        category_list = request.POST.getlist('category')
        summary = request.POST.get('summary').strip()
        author = request.user
        tags = request.POST.get('tags').strip()

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
        title = request.POST.get('title').strip()
        image = request.FILES.get('image')        
        category_list = request.POST.getlist('category')
        summary = request.POST.get('summary').strip()
        author = request.user
        tags = request.POST.get('tags').strip()
        
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
        name = request.POST.get('name').strip()
        image = request.FILES.get('image')
        description = request.POST.get('description').strip()
        price = request.POST.get('price').strip()
        category = request.POST.get('category').strip()

        try:
            category = get_object_or_404(ProductCategory, slug = category)
        except Http404:
            messages.error(self.request, "Failed. Invalid category")
            return redirect('csc_admin:create_product')
        
        self.model.objects.create(name = name, image = image, description = description, price = price, category = category)
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
    fields = ["image", "name", "description", "price", "category"]
    template_name = "admin_product/update.html"
    
    def get_success_url(self, *kwargs):
        return reverse_lazy("csc_admin:product", kwargs = {"slug" : self.object.slug})
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name').strip()
        image = request.FILES.get('image')
        description = request.POST.get('description').strip()
        price = request.POST.get('price').strip()
        category = request.POST.get('category').strip()

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


def get_product_categories(request):
    categories = list(ProductCategory.objects.all().values('slug', 'name'))
    return JsonResponse({"categories": categories})


@method_decorator(csrf_exempt, name="dispatch")
class AddProductCategoryView(BaseAdminCscProductView, CreateView):
    model = ProductCategory
    slug_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        category = request.POST.get('category').strip()

        print(category)

        self.model.objects.create(name = category)

        return JsonResponse({'status': 'success'})


@method_decorator(csrf_exempt, name="dispatch")
class EditProductCategoryView(BaseAdminCscProductView, UpdateView):
    model = ProductCategory
    slug_url_kwarg = 'slug'

    def post(self, request, *args, **kwargs):
        category = request.POST.get('category').strip()


        self.object = self.get_object()
        self.object.name = category
        self.object.save()

        return JsonResponse({'status': 'success'})
    

class DeleteProductCategoryView(BaseAdminCscProductView, View):
    model = ProductCategory

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            pass

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        return JsonResponse({'status': 'success'})


class ProductEnquiryListView(BaseAdminCscProductView, ListView):
    model = AdminProductEnquiry
    queryset = model.objects.all().order_by('-created')
    context_object_name = "enquiries"
    template_name = "admin_product/enquiry_list.html"


class DeleteProductEnquiryView(BaseAdminCscProductView, View):
    model = AdminProductEnquiry
    success_url = redirect_url = reverse_lazy("csc_admin:product_enquiries")

    def get_object(self):
        try:
            return get_object_or_404(AdminProductEnquiry, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Product Enquiry")
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()        
            self.object.delete()
            messages.success(self.request, "Successfully deleted product enquiry.")
            return redirect(self.success_url)
        except Exception as e:
            print(f"Error: {e}")
            return redirect(self.redirect_url)
##################################### PRODUCT END #####################################

##################################### CSC CENTER START #####################################

@method_decorator(never_cache, name="dispatch")
class BaseAdminCscCenterView(BaseAdminView):
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


class ListCscCenterRequestView(BaseAdminCscCenterView, ListView):
    queryset = CscCenter.objects.filter(is_active = False, status = "Not Viewed").order_by("-created")
    template_name = 'admin_csc_center/request_list.html'
    context_object_name = "csc_centers"


class CscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/request_detail.html'
    slug_url_kwarg = 'slug'


class RejectCscCenterRequestView(BaseAdminCscCenterView, UpdateView):
    success_url = reverse_lazy('csc_admin:csc_center_requests')
    redirect_url = success_url
    fields = ['status']

    def get_redirect_url(self):
        try:
            self.object = self.get_object()
            return reverse_lazy('csc_admin:csc_center_request', kwargs={'slug': self.object.slug}) if self.object else None
        except Http404:
            return redirect(self.redirect_url)    
        except Exception as e:
            print("Error: {e}")

    def post(self, request, *args, **kwargs):
        rejection_reason = request.POST.get('rejection_reason')
        rejection_reason = rejection_reason.strip() if rejection_reason else None
        self.object = self.get_object()

        if rejection_reason:
            self.object.status = "Rejected"
            self.object.save()

            CscCenterAction.objects.create(csc_center = self.object, rejection_reason = rejection_reason)
            messages.success(request, "Request Rejected")
            return redirect(self.get_success_url())
        else:
            messages.error(request, "Request rejection failed.")
            return redirect(self.get_redirect_url())


class ListRejectedCscCenterRequestView(BaseAdminCscCenterView, ListView):
    model = CscCenterAction
    queryset = model.objects.exclude(rejection_reason = "").order_by("-created")
    template_name = 'admin_csc_center/rejected_list.html'
    context_object_name = "csc_centers"


class RejectedCscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):
    model = CscCenterAction
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/rejected_detail.html'
    slug_url_kwarg = 'slug'


class CancelCscCenterRejectionView(BaseAdminCscCenterView, UpdateView):
    fields = ['status']
    success_url = reverse_lazy('csc_admin:rejected_csc_centers')
    redirect_url = success_url

    def get_redirect_url(self):
        try:
            return reverse_lazy('csc_admin:rejected_csc_center', kwargs = {'slug' : self.kwargs.get('slug')})
        except Http404:
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.status = "Not Viewed"
            self.object.save()
            try:
                csc_center_action = get_object_or_404(CscCenterAction, csc_center__slug = self.kwargs.get('slug'))
                csc_center_action.delete()
            except Http404:
                pass
            messages.success(request, "Cancelled csc center request rejection")
            return redirect(self.get_success_url())
        except Exception as e:
            print("Error: ", e)
            messages.error(request, "Cancelling csc center request rejection failed")
            return redirect(self.get_redirect_url())


class ReturnCscCenterRequestView(BaseAdminCscCenterView, UpdateView):
    success_url = reverse_lazy('csc_admin:csc_center_requests')
    redirect_url = success_url
    fields = ['status']

    def get_redirect_url(self):
        try:
            self.object = self.get_object()
            return reverse_lazy('csc_admin:csc_center_request', kwargs={'slug': self.object.slug}) if self.object else None
        except Http404:
            return redirect(self.redirect_url)    
        except Exception as e:
            print("Error: {e}")

    def post(self, request, *args, **kwargs):
        feedback = request.POST.get('feedback')
        feedback = feedback.strip() if feedback else None
        self.object = self.get_object()

        if feedback:
            self.object.status = "Returned"
            self.object.save()

            CscCenterAction.objects.create(csc_center = self.object, feedback = feedback)
            messages.success(request, "Request Returned")
            return redirect(self.get_success_url())
        else:
            messages.error(request, "Request returning failed.")
            return redirect(self.get_redirect_url())


class ListReturnedCscCenterRequestView(BaseAdminCscCenterView, ListView):
    model = CscCenterAction
    queryset = model.objects.exclude(feedback = "").order_by('-created')
    template_name = 'admin_csc_center/returned_list.html'
    context_object_name = "csc_centers"


class ReturnedCscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):
    model = CscCenterAction
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/returned_detail.html'
    slug_url_kwarg = 'slug'


class CancelCscCenterReturnView(BaseAdminCscCenterView, UpdateView):
    fields = ['status']
    success_url = reverse_lazy('csc_admin:returned_csc_centers')
    redirect_url = success_url

    def get_redirect_url(self):
        try:
            return reverse_lazy('csc_admin:returned_csc_center', kwargs = {'slug' : self.kwargs.get('slug')})
        except Http404:
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.status = "Not Viewed"
            self.object.save()
            try:
                csc_center_action = get_object_or_404(CscCenterAction, csc_center__slug = self.kwargs.get('slug'))
                csc_center_action.delete()
            except Http404:
                pass
            messages.success(request, "Cancelled csc center request return")
            return redirect(self.get_success_url())
        except Exception as e:
            print("Error: ", e)
            messages.error(request, "Cancelling csc center request return failed")
            return redirect(self.get_redirect_url())


class ApproveCscCenterRequestView(BaseAdminCscCenterView, UpdateView):
    success_url = reverse_lazy('csc_admin:csc_center_requests')
    fields = ['status']


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.status = "Approved"
        self.object.save()

        payment_link = f"http://www.example.com/"
        
        if self.object.email and payment_link:
            
            send_confirm_creation(center = self.object, payment_link = payment_link)

        messages.success(request, "Request Approved")
        return redirect(self.get_success_url())
    

class ListApprovedCscCenterRequestView(BaseAdminCscCenterView, ListView):    
    queryset = CscCenter.objects.filter(status = "Approved").order_by('-created')
    template_name = 'admin_csc_center/approved_list.html'
    context_object_name = "csc_centers"


class ApprovedCscCenterRequestDetailView(BaseAdminCscCenterView, DetailView):    
    context_object_name = 'csc_center'
    template_name = 'admin_csc_center/approved_detail.html'
    slug_url_kwarg = 'slug'


class CancelCscCenterApprovalView(BaseAdminCscCenterView, UpdateView):
    fields = ['status']
    success_url = reverse_lazy('csc_admin:approved_csc_centers')
    redirect_url = success_url

    def get_redirect_url(self):
        try:
            return reverse_lazy('csc_admin:approved_csc_center', kwargs = {'slug' : self.kwargs.get('slug')})
        except Http404:
            return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.status = "Not Viewed"
            self.object.save()        
            messages.success(request, "Cancelled csc center request approval")
            return redirect(self.get_success_url())
        except Exception as e:
            print("Error: ", e)
            messages.error(request, "Cancelling csc center request approval Failed")
            return redirect(self.get_redirect_url())


class ListCscCenterView(BaseAdminCscCenterView, ListView):
    template_name = "admin_csc_center/list.html"
    ordering = ['name']
    context_object_name = 'centers'
    queryset = CscCenter.objects.all().order_by('name')

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            state = request.GET.get('state', None)
            state = state.strip() if state else None

            district = request.GET.get('district', None)
            district = district.strip() if district else None

            block = request.GET.get('block', None)
            block = block.strip() if block else None

            if state and district and block:
                kwargs = {'state__pk': state, 'district__pk': district, 'block__pk': block}
            elif state and district:
                kwargs = {'state__pk': state, 'district__pk': district}
            elif state:
                kwargs = {'state__pk': state}

            kwargs['is_active'] = True
            center_list = []
            centers = CscCenter.objects.filter(**kwargs).order_by('name')

            data = {}

            if state:
                districts = list(District.objects.filter(state__pk = state).values('id', 'district')) if state else None
                data['districts'] = districts
            if state and district:
                blocks = list(Block.objects.filter(state__pk = state, district__pk = district).values('id', 'block')) if state and district else None
                data['blocks'] = blocks

            for count, center in enumerate(centers):
                center_list.append({
                    'count': count + 1,
                    'name': center.name,
                    'owner': center.owner,
                    'partial_address': center.partial_address,
                    'email': center.email,
                    'contact_number': center.contact_number})
            data['centers'] = center_list
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)


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
        name = request.POST.get('name').strip()
        type = request.POST.get('type').strip()
        keywords = request.POST.getlist('keywords')

        state = request.POST.get('state').strip()
        district = request.POST.get('district').strip()
        block = request.POST.get('block').strip()
        location = request.POST.get('location').strip()
        zipcode = request.POST.get('zipcode').strip()
        landmark_or_building_name = request.POST.get('landmark_or_building_name').strip()
        street = request.POST.get('address').strip()
        logo = request.FILES.get('logo') # dropzone
        banners = request.FILES.getlist('banner') # dropzone
        description = request.POST.get('description').strip()
        owner = request.POST.get('owner').strip()
        email = request.POST.get('email').strip()
        website = request.POST.get('website') # optional.strip()
        contact_number = request.POST.get('contact_number').strip()
        mobile_number = request.POST.get('mobile_number').strip()
        whatsapp_number = request.POST.get('whatsapp_number').strip()
        services = request.POST.getlist('services')
        products = request.POST.getlist('products')

        show_opening_hours = request.POST.get('show_opening_hours')
        if show_opening_hours: 
            show_opening_hours = show_opening_hours.strip()

        mon_opening_time = request.POST.get('mon_opening_time').strip() if show_opening_hours else None #timefield
        tue_opening_time = request.POST.get('tue_opening_time').strip() if show_opening_hours else None #timefield
        wed_opening_time = request.POST.get('wed_opening_time').strip() if show_opening_hours else None #timefield
        thu_opening_time = request.POST.get('thu_opening_time').strip() if show_opening_hours else None #timefield
        fri_opening_time = request.POST.get('fri_opening_time').strip() if show_opening_hours else None #timefield
        sat_opening_time = request.POST.get('sat_opening_time').strip() if show_opening_hours else None #timefield
        sun_opening_time = request.POST.get('sun_opening_time').strip() if show_opening_hours else None #timefield

        mon_closing_time = request.POST.get('mon_closing_time').strip() if show_opening_hours else None #timefield
        tue_closing_time = request.POST.get('tue_closing_time').strip() if show_opening_hours else None #timefield
        wed_closing_time = request.POST.get('wed_closing_time').strip() if show_opening_hours else None #timefield
        thu_closing_time = request.POST.get('thu_closing_time').strip() if show_opening_hours else None #timefield
        fri_closing_time = request.POST.get('fri_closing_time').strip() if show_opening_hours else None #timefield
        sat_closing_time = request.POST.get('sat_closing_time').strip() if show_opening_hours else None #timefield
        sun_closing_time = request.POST.get('sun_closing_time').strip() if show_opening_hours else None #timefield

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
        if show_social_media_links:
            show_social_media_links = show_social_media_links.strip()

        social_medias = request.POST.getlist('social_medias') if show_social_media_links else None # manytomany
        social_links = request.POST.getlist('social_links') if show_social_media_links else None # manytomany

        latitude = request.POST.get('latitude').strip()
        longitude = request.POST.get('longitude').strip()

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
            street = street, logo = logo,
            description = description, contact_number = contact_number,
            owner = owner, email = email, website = website, 
            mobile_number = mobile_number, whatsapp_number = whatsapp_number,
            mon_opening_time = mon_opening_time, tue_opening_time = tue_opening_time, 
            wed_opening_time = wed_opening_time, thu_opening_time = thu_opening_time, 
            fri_opening_time = fri_opening_time, sat_opening_time = sat_opening_time, 
            sun_opening_time = sun_opening_time, mon_closing_time = mon_closing_time, 
            tue_closing_time = tue_closing_time, wed_closing_time = wed_closing_time, 
            thu_closing_time = thu_closing_time, fri_closing_time = fri_closing_time, 
            sat_closing_time = sat_closing_time, sun_closing_time = sun_closing_time, 
            latitude = latitude, longitude = longitude
        )

        if not User.objects.filter(email = email).exists():
            User.objects.create_user(username = email, email = email, password = contact_number)            

        messages.success(request, "Added CSC center")      
        
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

class DetailCscCenterView(BaseAdminCscCenterView, DetailView):
    template_name = "admin_csc_center/detail.html"
    context_object_name = 'center'


@method_decorator(never_cache, name="dispatch")
class UpdateCscCenterView(BaseAdminCscCenterView, UpdateView):
    template_name = 'admin_csc_center/update.html'
    context_object_name = 'center'
    fields = "__all__"
    slug_url_kwarg = 'slug'

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

        name = request.POST.get('name').strip()
        type = request.POST.get('type').strip()
        keywords = request.POST.getlist('keywords')

        state = request.POST.get('state').strip()
        district = request.POST.get('district').strip()
        block = request.POST.get('block').strip()
        location = request.POST.get('location').strip()
        zipcode = request.POST.get('zipcode').strip()
        landmark_or_building_name = request.POST.get('landmark_or_building_name').strip()
        street = request.POST.get('address').strip()
        logo = request.FILES.get('logo')
        banners = request.FILES.getlist('banner')
        description = request.POST.get('description').strip()
        owner = request.POST.get('owner').strip()
        email = request.POST.get('email').strip()
        website = request.POST.get('website').strip()
        contact_number = request.POST.get('contact_number').strip()
        mobile_number = request.POST.get('mobile_number').strip()
        whatsapp_number = request.POST.get('whatsapp_number').strip()
        services = request.POST.getlist('services')
        products = request.POST.getlist('products')

        show_opening_hours = request.POST.get('show_opening_hours').strip()

        mon_opening_time = request.POST.get('mon_opening_time').strip() if show_opening_hours else None #timefield
        tue_opening_time = request.POST.get('tue_opening_time').strip() if show_opening_hours else None #timefield
        wed_opening_time = request.POST.get('wed_opening_time').strip() if show_opening_hours else None #timefield
        thu_opening_time = request.POST.get('thu_opening_time').strip() if show_opening_hours else None #timefield
        fri_opening_time = request.POST.get('fri_opening_time').strip() if show_opening_hours else None #timefield
        sat_opening_time = request.POST.get('sat_opening_time').strip() if show_opening_hours else None #timefield
        sun_opening_time = request.POST.get('sun_opening_time').strip() if show_opening_hours else None #timefield
        mon_closing_time = request.POST.get('mon_closing_time').strip() if show_opening_hours else None #timefield
        tue_closing_time = request.POST.get('tue_closing_time').strip() if show_opening_hours else None #timefield
        wed_closing_time = request.POST.get('wed_closing_time').strip() if show_opening_hours else None #timefield
        thu_closing_time = request.POST.get('thu_closing_time').strip() if show_opening_hours else None #timefield
        fri_closing_time = request.POST.get('fri_closing_time').strip() if show_opening_hours else None #timefield
        sat_closing_time = request.POST.get('sat_closing_time').strip() if show_opening_hours else None #timefield
        sun_closing_time = request.POST.get('sun_closing_time').strip() if show_opening_hours else None #timefield

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

        show_social_media_links = request.POST.get('show_social_media_links').strip()

        social_medias = request.POST.getlist('social_medias') if show_social_media_links else None # manytomany
        social_links = request.POST.getlist('social_links') if show_social_media_links else None # manytomany

        latitude = request.POST.get('latitude').strip()
        longitude = request.POST.get('longitude').strip()

        try:
            type = get_object_or_404(CscNameType, slug = type)
        except Http404:
            messages.error(request, 'Invalid CSC Name Type')
            return redirect(reverse_lazy('csc_admin:update_csc'))

        try:
            state = get_object_or_404(State, pk = state)
        except Http404:
            messages.error(request, 'Invalid State')
            return redirect(reverse_lazy('csc_admin:update_csc'))

        try:
            district = get_object_or_404(District, pk = district)
        except Http404:
            messages.error(request, 'Invalid District')
            return redirect(reverse_lazy('csc_admin:update_csc'))
        
        try:
            block = get_object_or_404(Block, pk = block)
        except Http404:
            messages.error(request, 'Invalid Block')
            return redirect(reverse_lazy('csc_admin:update_csc'))
        
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

        if banners:
            for banner in banners:
                banner_obj, created = Banner.objects.get_or_create(csc_center = self.object, banner_image = banner)
                self.object.banners.add(banner_obj)
            self.object.save()


                

        self.object.description = description
        self.object.owner = owner
        self.object.email = email
        self.object.website = website
        self.object.contact_number = contact_number
        self.object.mobile_number = mobile_number
        self.object.whatsapp_number = whatsapp_number        

        self.object.show_opening_hours = True if show_opening_hours else False
        self.object.show_social_media_links = True if show_social_media_links else False

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
            else:
                self.object.social_media_links.clear()
                self.object.save()
        else:
            self.object.social_media_links.clear()
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


@method_decorator(csrf_exempt, name="dispatch")
class RemoveSocialMediaLinkView(BaseAdminCscCenterView, UpdateView):
    fields = ["social_media_links"]
    pk_url_kwarg = 'slug'

    def get_object(self, **kwargs):
        try:
            return get_object_or_404(CscCenter, slug = self.kwargs['slug'])
        except Http404:
            return JsonResponse({"message": "Error. Invalid CSC Center"})

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        social_media_id = request.POST.get('social_media_id').strip()

        try:
            social_media_link = get_object_or_404(SocialMediaLink, pk = social_media_id)
        except Http404:
            return JsonResponse({"message": "Error. No such social media object"})
        
        self.object.social_media_links.remove(social_media_link)
        self.object.save()
        
        return JsonResponse({'message': 'success'})
    

class CscOwnersListView(BaseAdminCscCenterView, ListView):
    queryset = CscCenter.objects.all().order_by("owner")
    template_name = "admin_csc_center/owners_list.html"
    context_object_name = 'csc_centers'

    def get_queryset(self):
        try:
            list_centers = self.queryset        
            for center in self.queryset:
                while list_centers.filter(email = center.email).count() > 1:
                    removing_center_pk = list_centers.filter(email = center.email).last().pk
                    list_centers = list_centers.exclude(pk = removing_center_pk)            
            return list_centers
        except Exception as e:
            print("Error: ", e)

    def get(self, request, *args, **kwargs):
        list_centers = self.get_queryset()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            kwargs = {}
            data = {}

            state = self.request.GET.get("state")
            district = self.request.GET.get("district")
            block = self.request.GET.get("block")

            if state:
                state = state.strip()
                kwargs['state__pk'] = state
                data['districts'] = list(District.objects.filter(state__pk = state).values('id', 'district'))

                if district:
                    district = district.strip()
                    kwargs['district__pk'] = district
                    data['blocks'] = list(Block.objects.filter(state__pk = state, district__pk = district).values('id', 'block'))

                    if block:
                        block = block.strip()
                        kwargs['block__pk'] = block


            data['csc_centers'] = list(list_centers.filter(**kwargs).values('owner', 'email', 'contact_number', 'mobile_number', 'whatsapp_number')) if kwargs else None            

            return JsonResponse(data)
        return super().get(request, *args, **kwargs)



# Nuclear
class GetDistrictView(View):
    def get(self, request, *args, **kwargs):
        state_id = request.GET.get('state_id').strip()
        districts = list(District.objects.filter(state__pk=state_id).values())
        return JsonResponse({"districts": districts}, safe=False)
    

class GetBlockView(View):
    def get(self, request, *args, **kwargs):
        district_id = request.GET.get('district_id').strip()
        state_id = request.GET.get('state_id').strip()
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
        state = request.POST.get('state').title().strip()

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
        
        state = request.POST.get('state').title().strip()

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
        state = request.POST.get('state').strip()
        districts = request.POST.get('districts').strip()
        
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

        state = request.POST.get('state').strip()
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
        state = request.POST.get('state').strip()
        district = request.POST.get('district').strip()
        blocks = request.POST.get('blocks').strip()
        
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

        state = request.POST.get('state').strip()
        district = request.POST.get('district').strip()
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
        keyword = request.POST.get('keyword').strip()

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
        
        keyword = request.POST.get('keyword').strip()

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
        name_type = request.POST.get('name_type').strip()

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
        
        name_type = request.POST.get('name_type').strip()

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

class BasePosterView(BaseAdminView):
    model = Poster
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poster_page'] = True
        return context
    

class PosterListView(BasePosterView, ListView):
    template_name = 'admin_poster/list.html'
    queryset = Poster.objects.all()
    context_object_name = 'posters'


class PosterDetailView(BasePosterView, DetailView):
    template_name = 'admin_poster/detail.html'
    context_object_name = 'poster'
    slug_url_kwarg = 'slug'

class CreatePosterView(BasePosterView, CreateView):
    fields = ["title", "poster", "state", "service"]
    template_name = 'admin_poster/create.html'
    success_url = reverse_lazy('csc_admin:posters')
    redirect_url = reverse_lazy('csc_admin:create_poster')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['states'] = State.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title').strip()
        poster = request.FILES.get('poster')
        state_id = request.POST.get('state').strip()
        service_slug = request.POST.get('service').strip() 

        try:
            state = get_object_or_404(State, pk = state_id)
        except Http404:
            messages.error(request, 'Invalid State')
            return redirect(self.redirect_url)
        
        try:
            service = get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(request, 'Invalid Service')
            return redirect(self.redirect_url)

        if title:
            self.poster = self.model.objects.create(title = title, poster = poster, state = state, service = service)            
            messages.success(request, 'Added Poster')
            return redirect(self.success_url)
        else:
            messages.warning(request, 'Please provide the poster title.')
            return redirect(self.redirect_url)
        

class DeletePosterView(BasePosterView, View):
    success_url = reverse_lazy('csc_admin:posters')
    redirect_url = success_url

    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(self.model, slug = self.kwargs['slug'])
            self.object.delete()
            messages.success(request, "Poster Deleted.")
            return redirect(self.success_url)
        except Http404:
            messages.error(request, 'Invalid Poster')
            return redirect(self.redirect_url)
        

class UpdatePosterView(BasePosterView, UpdateView):
    fields = ["title", "poster", "state", "service"]
    template_name = 'admin_poster/update.html'
    success_url = reverse_lazy('csc_admin:posters')
    redirect_url = success_url
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['states'] = State.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        title = request.POST.get('title').strip()
        poster = request.FILES.get('poster')
        state_id = request.POST.get('state').strip()
        service_slug = request.POST.get('service').strip() 

        try:
            state = get_object_or_404(State, pk = state_id)
        except Http404:
            messages.error(request, 'Invalid State')
            return redirect(self.redirect_url)
        
        try:
            service = get_object_or_404(Service, slug = service_slug)
        except Http404:
            messages.error(request, 'Invalid Service')
            return redirect(self.redirect_url)

        if not title:
            messages.warning(request, 'Title is required.')            
            return redirect(self.redirect_url)
        
        if not state:
            messages.warning(request, 'State is required.')            
            return redirect(self.redirect_url)
        
        if not service:
            messages.warning(request, 'Service is required.')            
            return redirect(self.redirect_url)
        
        if not poster:
            poster = self.object.poster

        self.object.title = title
        self.object.poster = poster
        self.object.state = state
        self.object.service = service
        self.object.save()

        messages.success(request, 'Updated Poster')
        return redirect(self.get_success_url())
            

################# Profile ##############

class MyProfileView(BaseAdminView, TemplateView):
    model = User
    template_name = "admin_profile/my_profile.html"
    success_url = reverse_lazy('csc_admin:my_profile')
    redirect_url = success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_page"] = True
        return context
    
    def get_object(self):
        try:
            return get_object_or_404(User, email = self.request.user.email)
        except:
            messages.error(self.request, 'Unauthorized user')
            return redirect(self.redirect_url)
    

class UpdateProfileView(MyProfileView, UpdateView):        
    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            image = request.FILES.get('image')
            name = request.POST.get('name').strip().title()
            phone = request.POST.get('phone').strip()
            email = request.POST.get('email').strip().lower()
            notes = request.POST.get('notes').strip()

            if not email:
                messages.error(request, "Email is required")
                return redirect(self.redirect_url)

            if name:
                name_parts = name.split(' ')

                first_name = name_parts[0] if len(name_parts) > 0 else None
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else None

                self.object.first_name = first_name
                self.object.last_name = last_name            
                self.object.notes = notes            

            
            if  phone.isnumeric():
                self.object.phone = phone
            
            if image:
                self.object.image = image

            self.object.save()

            current_email = self.object.email

            if email != current_email:
                user_csc_centers = CscCenter.objects.filter(email = current_email)
                for csc_center in user_csc_centers:
                    csc_center.email = email
                    csc_center.save()
                self.object.email = email
                self.object.save()

            messages.success(request, "Updated user profile details.")
            return redirect(self.get_success_url())
        except Exception as e:
            print(f"Exception: {e}")
            return redirect(self.redirect_url)


class ChangePasswordView(MyProfileView, UpdateView):
    success_url = reverse_lazy('authentication:login')
    redirect_url = reverse_lazy('csc_admin:my_profile')

    # def get_object(self):
    #     try:
    #         return get_object_or_404(User, email = self.request.user.email)
    #     except:
    #         messages.error(self.request, 'Unauthorized user')
    #         return redirect(self.redirect_url)

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()

            current_password = request.POST.get('current_password').strip()
            new_password = request.POST.get('new_password').strip()
            confirm_password = request.POST.get('confirm_password').strip()

            user = authenticate(request, username = request.user.username, password = current_password)

            if user is not None and new_password == confirm_password:
                self.object.set_password(new_password)
                self.object.save()
                messages.success(request, "Password Updated. Please login again with your new password")
                logout(request)
                return redirect(self.get_success_url())
            
            if user is None:
                error_msg = "The current password you entered is incorrect"
            elif new_password != confirm_password:
                error_msg = "New passwords are not matching"
            else:
                error_msg = "Something went wrong."

            messages.error(request, error_msg)
            return redirect(self.redirect_url)
        
        except Exception as e:
            print(f"Exception: {e}")
            return redirect(self.redirect_url)
    


############# FAQ START ##############

class BaseFaqView(BaseAdminView, View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faq_page'] = True
        return context

class CreateFaqView(BaseFaqView, CreateView):
    model = Faq
    success_url = reverse_lazy('csc_admin:add_faq')
    fields = ["question", "answer"]
    template_name = "admin_faq/create.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "FAQ created successfully")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "FAQ creation failed")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field - {field}: {error}")
        return super().form_invalid(form)
    

class ListFaqView(BaseFaqView, ListView):
    model = Faq
    template_name = "admin_faq/list.html"
    context_object_name = "faqs"
    queryset = model.objects.all()


class FaqDetailView(BaseFaqView, DetailView):
    model = Faq
    template_name = "admin_faq/detail.html"
    context_object_name = "faq"
    slug_url_kwarg = 'slug'


class UpdateFaqView(BaseFaqView, UpdateView):
    model = Faq
    fields = ["question", "answer"]
    template_name = "admin_faq/update.html"
    context_object_name = "faq"
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        try:
            return reverse_lazy('csc_admin:faq', kwargs={'slug': self.kwargs.get('slug')})
        except Http404:
            return reverse_lazy('csc_admin:faqs')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "FAQ updated successfully")
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "FAQ updation failed")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error on field - {field}: {error}")
        return super().form_invalid(form)
    

class DeleteFaqView(BaseFaqView, View):
    model = Faq
    success_url = reverse_lazy('csc_admin:faqs')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(Faq, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid FAQ")
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "FAQ deleted successfully")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(request, "FAQ deletion failed")
            print(f"Error: {e}")
            return redirect(self.redirect_url)

############# FAQ END ##############

############### ENQUIRY START ###############

class EnquiryBaseView(BaseAdminView):
    model = Enquiry

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enquiry_page'] = True
        return context


class EnquiryListView(EnquiryBaseView, ListView):
    template_name = 'admin_enquiry/list.html'
    queryset = Enquiry.objects.all()
    context_object_name = 'enquiries'


class DeleteEnquiryView(EnquiryBaseView, View):
    success_url = reverse_lazy('csc_admin:enquiries')
    redirect_url = success_url

    def get_object(self):
        try:
            return get_object_or_404(Enquiry, slug=self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Enquiry")
            return redirect(self.redirect_url)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            self.object.delete()
            messages.success(request, "Enquiry deleted successfully")
            return redirect(self.success_url)
        except Exception as e:
            print(F"Error: {e}")
            return redirect(self.redirect_url)
        

class CscCenterEnquiriesListView(EnquiryBaseView, ListView):
    model = CscCenter
    context_object_name = 'csc_centers'
    template_name = "admin_enquiry/list_centers_enquiries.html"

    def get_queryset(self):
        data = []
        for csc_center in self.model.objects.all():
            service_enquiries_count = ServiceEnquiry.objects.filter(csc_center = csc_center).count()
            product_enquiries_count = ProductEnquiry.objects.filter(csc_center = csc_center).count()
            if service_enquiries_count > 0 or product_enquiries_count > 0:
                data.append({
                    'name': csc_center.full_name,
                    'service_enquiries_count': ServiceEnquiry.objects.filter(csc_center = csc_center).count(),
                    'product_enquiries_count': ProductEnquiry.objects.filter(csc_center = csc_center).count()
                })
        return data
        
############### ENQUIRY END ###############

class PaymentHistoryBaseView(BaseAdminView):
    model = Payment

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['csc_center_page'] = True
        return context

class PaymentHistoryListView(PaymentHistoryBaseView, ListView):
    queryset = Payment.objects.all().order_by('-created')
    template_name = "admin_csc_center/list_payment_history.html"
    context_object_name = 'payments'


class PaymentHistoryDetailView(PaymentHistoryBaseView, DetailView):
    context_object_name = 'payment'
    template_name = "admin_csc_center/detail_payment_history.html"

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        service_charge = 50
        context['service_charge'] = service_charge
        self.object = self.get_object()
        context['total'] = self.object.amount + service_charge
        return context
    

# Price
class AddPriceView(BaseAdminView, CreateView):
    model = Price
    fields = ("price", "from", "to", "description")

    def send_offer_mail(self, center, price):
        subject = 'Exclusive Offer for CSC Center Registration'
        from_email = 'w3digitalpmna@gmail.com'
        to_email = [center.email]

        html_content = render_to_string('admin_email_templates/offer.html', {
            'customer_name': center.owner,
            'offer_price': price.offer_price,
            'offer_start_date': price.from_date,
            'offer_expiry_date': price.to_date,
            'sender_mail': from_email
        })

        email = EmailMultiAlternatives(subject, '', from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()


    def post(self, request, *args, **kwargs):
        try:
            if request.headers.get('X-Requested-With') == "XMLHttpRequest":
                try:
                    price = request.POST.get("price")
                    price = price.strip() if price else None
                    from_date = request.POST.get("from")
                    from_date = from_date.strip() if from_date else None
                    to_date = request.POST.get("to")
                    to_date = to_date.strip() if to_date else None
                    description = request.POST.get("description")
                    description = description.strip() if description else None

                    if from_date and to_date:
                        starting_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                        ending_date = datetime.strptime(to_date, '%Y-%m-%d').date()                        
                        if starting_date < timezone.now().date() or ending_date < starting_date:
                            return JsonResponse({"error": "Invalid date range"}, status=400)
                        self.object = Price.objects.all().first() if Price.objects.all().count() > 0 else None  
                        price_obj = self.object


                        if self.object:                            
                            if self.object.offer_price == float(price) and self.object.from_date == starting_date and self.object.to_date == ending_date and self.object.description == description:
                                return JsonResponse({"error": "Price already exists"})
                                                        
                            self.object.offer_price = price
                            self.object.from_date = from_date
                            self.object.to_date = to_date
                            self.object.description = description
                            self.object.save()
                        else:
                            default_amount = 500
                            price_obj = Price.objects.create(price=default_amount, offer_price = price, from_date = from_date, to_date = to_date, description = description)                            

                        list_centers = CscCenter.objects.all().order_by("owner")        
                        for center in CscCenter.objects.all().order_by("owner"):
                            while list_centers.filter(email = center.email).count() > 1:
                                removing_center_pk = list_centers.filter(email = center.email).last().pk
                                list_centers = list_centers.exclude(pk = removing_center_pk)                                        

                        # for center in list_centers:
                        #     send_offer_mail(center, price)

                        center = CscCenter.objects.get(name = "RBC")
                        self.send_offer_mail(center, price_obj)
                        
                    else:
                        for price_obj in Price.objects.all():
                            price_obj.delete()
                        Price.objects.create(price=price)
                        
                    return JsonResponse({"status": "success"})
                except Exception as e:
                    print(e)
                    return JsonResponse({"status": "error"})
        except Exception as e:
            print(f"Error: {e}")
        return super().post(request, *args, **kwargs)
