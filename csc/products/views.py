from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View
from django.http import Http404, JsonResponse

from .models import Product, Category
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


class ProductDetailView(ProductBaseView, DetailView):
    template_name = 'products/detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    redirect_url = reverse_lazy('products:products')


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
                'get_absolute_url': product.get_absolute_url
                })
        return JsonResponse({"message": "success", "products": product_list})
    