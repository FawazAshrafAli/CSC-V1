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
import re

from .forms import (
    CreateServiceForm, UpdateServiceForm, CreateBlogForm,
    UpdateBlogForm
    )

from csc_center.models import CscCenter, State, District, Block
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

##################################### CSC CENTER START #####################################

@method_decorator(never_cache, name="dispatch")
class BaseAdminCscCenterView(BaseAdminView, View):
    model = CscCenter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'states': State.objects.all().order_by('state'),
            'districts': District.objects.all().order_by('district'),
            'blocks': Block.objects.all().order_by('block'),
            })
        return context


class ListCscCenter(BaseAdminCscCenterView, ListView):
    template_name = "admin_csc_center/list.html"


class AddCscCenter(BaseAdminCscCenterView, CreateView):
    template_name = 'admin_csc_center/create.html'
    success_url = reverse_lazy('csc_admin:add_csc')
    fields = "__all__"

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['states'] = State.objects.all()
        return context


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
class EditStateView(BaseAdminCscCenterView, UpdateView):
    def post(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(State, pk = self.kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "State does not exist"}, status=400)
        
        state = request.POST.get('state').title()

        if not state:
            return JsonResponse({"error": "State is required"}, status=400)        

        if not State.objects.filter(state = state).exists():
            self.object.state = state
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)
        else:
            return JsonResponse({"error": "State already exists"}, safe=False)


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
        
        if not District.objects.filter(state = state, district = district).exists():
            self.object.state = state
            self.object.district = district
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)        
        else:            
            return JsonResponse({"error": f"District already exists for the state '{state}'"}, safe=False)
        

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

        if not Block.objects.filter(state = state, district = district, block = block).exists():
            self.object.state = state
            self.object.district = district
            self.object.block = block
            self.object.save()
            return JsonResponse({"status": "success"}, safe=False)

        else:            
            return JsonResponse({"error": f"Block already exists for the district '{district}' of state '{state}'"}, safe=False)
        

class DeleteStateView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(State, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "Block does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)
    

class DeleteDistrictView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(District, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "District does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)


class DeleteBlockView(BaseAdminCscCenterView, View):
    def get(self, request, *args, **kwargs):
        try:
            self.object = get_object_or_404(Block, pk = kwargs['pk'])
        except Http404:
            return JsonResponse({"error": "Block does not exist"}, safe=False)

        self.object.delete()
        return JsonResponse({"status": "success"}, safe=False)
##################################### CSC CENTER END #####################################