from django.urls import path
from .views import (
    AdminHomeView, ListServiceView, DetailServiceView, 
    UpdateServiceView, CreateServiceView, 
    DeleteServiceView, RemoveServiceImageView,

    BlogListView, BlogDetailView, CreateBlogView,
    UpdateBlogView, DeleteBlogView, RemoveBlogImageView,
    ChangeBlogStatusView,
    )

app_name = "csc_admin"

urlpatterns = [
    path("", AdminHomeView.as_view(), name="home"),

    path("services/", ListServiceView.as_view(), name="services"),
    path("service/<pk>", DetailServiceView.as_view(), name="service"),
    path("create_service/", CreateServiceView.as_view(), name="create_service"),
    path("update_service/<pk>", UpdateServiceView.as_view(), name="update_service"),
    path("delete_service/<pk>", DeleteServiceView.as_view(), name="delete_service"),
    path("remove_service_image/<pk>", RemoveServiceImageView.as_view(), name="remove_service_image"),

    path('blogs/', BlogListView.as_view(), name="blogs"),
    path('blog/<str:slug>', BlogDetailView.as_view(), name="blog"),
    path('create_blog/', CreateBlogView.as_view(), name="create_blog"),
    path('update_blog/<str:slug>', UpdateBlogView.as_view(), name="update_blog"),
    path('delete_blog/<str:slug>', DeleteBlogView.as_view(), name="delete_blog"),
    path("remove_blog_image/<pk>", RemoveBlogImageView.as_view(), name="remove_blog_image"),    
    path("change_blog_status/<str:slug>", ChangeBlogStatusView.as_view(), name="change_blog_status"),    

    ]
