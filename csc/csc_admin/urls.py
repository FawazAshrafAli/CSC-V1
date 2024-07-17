from django.urls import path
from .views import (
    AdminHomeView, ListServiceView, DetailServiceView, 
    UpdateServiceView, CreateServiceView, 
    DeleteServiceView, RemoveServiceImageView,

    BlogListView, BlogDetailView, CreateBlogView,
    UpdateBlogView, DeleteBlogView, RemoveBlogImageView,
    ChangeBlogStatusView, 

    AddCscCenter, GetDistrictView, GetBlockView,
    ListCscCenter,

    get_all_states, get_all_districts, get_all_blocks,
    GetDistrictDetailsView, GetBlockDetailsView,
    CreateStateView, CreateDistrictView, CreateBlockView,
    EditStateView, EditDistrictView, EditBlockView,
    DeleteStateView, DeleteDistrictView, DeleteBlockView
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

    path('csc_centers/', ListCscCenter.as_view(), name = "csc_centers"),
    path('add_csc/', AddCscCenter.as_view(), name = "add_csc"),
    path('get_districts/', GetDistrictView.as_view(), name="get_districts"),
    path('get_blocks/', GetBlockView.as_view(), name="get_blocks"),

    path('get_all_states/', get_all_states, name="get_all_states"),
    path('get_all_districts/', get_all_districts, name="get_all_districts"),
    path('get_all_blocks/', get_all_blocks, name="get_all_blocks"),

    path('get_district_detail/<int:pk>', GetDistrictDetailsView.as_view(), name="get_district_detail"),
    path('get_block_detail/<int:pk>', GetBlockDetailsView.as_view(), name="get_block_detail"),

    # Pop up box urls start
    path('add_state/', CreateStateView.as_view(), name="add_state"),
    path('edit_state/<int:pk>', EditStateView.as_view(), name="edit_state"),
    path('delete_state/<int:pk>', DeleteStateView.as_view(), name="delete_state"),

    path('add_district/', CreateDistrictView.as_view(), name="add_district"),
    path('edit_district/<int:pk>', EditDistrictView.as_view(), name="edit_district"),
    path('delete_district/<int:pk>', DeleteDistrictView.as_view(), name="delete_district"),

    path('add_block/', CreateBlockView.as_view(), name="add_block"),
    path('edit_block/<int:pk>', EditBlockView.as_view(), name="edit_block"),
    path('delete_block/<int:pk>', DeleteBlockView.as_view(), name="delete_block"),
    # Pop up box urls end
    ]
