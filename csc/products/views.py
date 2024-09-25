from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View
from django.http import Http404, JsonResponse
from django.contrib import messages

from .models import Product, Category
from csc_admin.models import ProductEnquiry
from services.models import Service

class ProductBaseView(View):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['services'] = Service.objects.all()
        context['product_page'] = True
        return context

class ProductListView(ProductBaseView, ListView):
    template_name = 'products/list.html'
    context_object_name = 'products'
    queryset = Product.objects.all()

class CategoryFilteredProductsListView(ProductBaseView, View):
    def get_queryset(self, **kwargs):
        if not  self.kwargs['slug']:
            return self.model.objects.all()
        return self.model.objects.filter(category__slug = self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        product_list = []
        products = self.get_queryset()
        for product in products:
            product_list.append({
                'name': product.name,
                'image': product.image.url if product.image else None,
                'price': product.price,
                "slug": product.slug                
                })
        return JsonResponse({"message": "success", "products": product_list})
    

# Create Product Enquiry (To super admin)
class CreateProductEnquiryView(ProductBaseView, View):
    success_url = redirect_url = reverse_lazy('products:products')

    def get_object(self):
        try:
            return get_object_or_404(self.model, slug = self.kwargs.get('slug'))
        except Http404:
            messages.error(self.request, "Invalid Product")
            return redirect(self.redirect_url)
    
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        print(f"The product is: {product}")

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
                return redirect(self.redirect_url)

        ProductEnquiry.objects.create(
            applicant_name=applicant_name, applicant_email=applicant_email,
            applicant_phone=applicant_phone, location=location, message=message,
            product = product
            )
        messages.success(request, "Product Enquiry submitted successfully")
        return redirect(self.success_url)
    