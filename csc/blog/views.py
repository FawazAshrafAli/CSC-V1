from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Blog

class BlogListView(ListView):
    model = Blog
    queryset = Blog.objects.all()
    context_object_name = 'blogs'
    template_name = 'blog/list.html'


class BlogDetailView(TemplateView):
    model = Blog
    context_object_name = 'blog'
    template_name = 'blog/detail.html'