from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, View
from .models import Blog, Category, Tag
import random

class BaseBlogView(View):
    model = Blog

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['blogs'] = Blog.objects.all()

        tag_list = list(Tag.objects.all())

        random_tags = random.sample(tag_list, 3)
        context['tags'] = random_tags
        print(random_tags)
        
        return context


class BlogListView(BaseBlogView, ListView):
    queryset = Blog.objects.all().order_by('created_at')
    context_object_name = 'blogs'
    template_name = 'blog/list.html'


class BlogDetailView(BaseBlogView, DetailView):    
    context_object_name = 'blog'
    template_name = 'blog/detail.html'