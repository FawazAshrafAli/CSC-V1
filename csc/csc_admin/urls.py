from django.urls import path
from .views import (
    AdminHomeView, ListServiceView, DetailServiceView, 
    UpdateServiceView, CreateServiceView, 
    DeleteServiceView, RemoveServiceImageView,

    BlogListView, BlogDetailView, CreateBlogView,
    UpdateBlogView, DeleteBlogView, RemoveBlogImageView,
    ChangeBlogStatusView, 

    CreateProductView, ProductListView, ProductDetailView,
    UpdateProductView, DeleteProductView,

    AddCscCenterView, GetDistrictView, GetBlockView,
    ListCscCenterView, DetailCscCenterView, UpdateCscCenterView,
    DeleteCscCenterView, RemoveCscCenterLogoView, RemoveCscCenterBannerView,
    RemoveSocialMediaLinkView,

    PosterListView, CreatePosterView, PosterDetailView,
    DeletePosterView,

    get_all_states, get_all_districts, get_all_blocks,
    get_csc_keywords, get_name_types,
    GetDistrictDetailsView, GetBlockDetailsView,
    CreateStateView, CreateDistrictView, CreateBlockView,
    EditStateView, EditDistrictView, EditBlockView,
    DeleteStateView, DeleteDistrictView, DeleteBlockView,
    CreateKeywordView, EditKeywordView, DeleteKeywordView,
    CreateCscNameTypeView, EditCscNameTypeView, DeleteCscNameTypeView,

    )

app_name = "csc_admin"

urlpatterns = [
    path("", AdminHomeView.as_view(), name="home"),

    path("services/", ListServiceView.as_view(), name="services"),
    path("service/<pk>", DetailServiceView.as_view(), name="service"),
    path("create_service/", CreateServiceView.as_view(), name="create_service"),
    path("update_service/<str:slug>", UpdateServiceView.as_view(), name="update_service"),
    path("delete_service/<str:slug>", DeleteServiceView.as_view(), name="delete_service"),
    path("remove_service_image/<pk>", RemoveServiceImageView.as_view(), name="remove_service_image"),

    path('blogs/', BlogListView.as_view(), name="blogs"),
    path('blog/<str:slug>', BlogDetailView.as_view(), name="blog"),
    path('create_blog/', CreateBlogView.as_view(), name="create_blog"),
    path('update_blog/<str:slug>', UpdateBlogView.as_view(), name="update_blog"),
    path('delete_blog/<str:slug>', DeleteBlogView.as_view(), name="delete_blog"),
    path("remove_blog_image/<pk>", RemoveBlogImageView.as_view(), name="remove_blog_image"),    
    path("change_blog_status/<str:slug>", ChangeBlogStatusView.as_view(), name="change_blog_status"),    

    path('create_product/', CreateProductView.as_view(), name = "create_product"),
    path('products/', ProductListView.as_view(), name = "products"),
    path('product/<str:slug>', ProductDetailView.as_view(), name = "product"),
    path('update_product/<str:slug>', UpdateProductView.as_view(), name = "update_product"),
    path('delete_product/<str:slug>', DeleteProductView.as_view(), name = "delete_product"),

    path('posters/', PosterListView.as_view(), name="posters"),
    path('poster/<str:slug>', PosterDetailView.as_view(), name="poster"),
    path('create_poster/', CreatePosterView.as_view(), name="create_poster"),
    path('delete_poster/<str:slug>', DeletePosterView.as_view(), name = "delete_poster"),

    path('csc_centers/', ListCscCenterView.as_view(), name = "csc_centers"),
    path('add_csc/', AddCscCenterView.as_view(), name = "add_csc"),
    path('csc_center/<str:slug>', DetailCscCenterView.as_view(), name = "csc_center"),
    path('update_csc/<str:slug>', UpdateCscCenterView.as_view(), name = "update_csc"),
    path('delete_csc/<str:slug>', DeleteCscCenterView.as_view(), name = "delete_csc"),
    path('remove_csc_logo/<str:slug>', RemoveCscCenterLogoView.as_view(), name = "remove_csc_logo"),
    path('remove_csc_banner/<str:slug>', RemoveCscCenterBannerView.as_view(), name = "remove_csc_banner"),
    path('remove_social_media_link/<str:slug>', RemoveSocialMediaLinkView.as_view(), name="remove_social_media_link"),

    path('get_districts/', GetDistrictView.as_view(), name="get_districts"),
    path('get_blocks/', GetBlockView.as_view(), name="get_blocks"),

    path('get_all_states/', get_all_states, name="get_all_states"),
    path('get_all_districts/', get_all_districts, name="get_all_districts"),
    path('get_all_blocks/', get_all_blocks, name="get_all_blocks"),
    path('get_csc_keywords/', get_csc_keywords, name="get_csc_keywords"),
    path('get_name_types/', get_name_types, name="get_name_types"),

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

    path('add_keyword/', CreateKeywordView.as_view(), name="add_keyword"),
    path('edit_keyword/<str:slug>', EditKeywordView.as_view(), name="edit_keyword"),
    path('delete_keyword/<str:slug>', DeleteKeywordView.as_view(), name="delete_keyword"),

    path('add_name_type/', CreateCscNameTypeView.as_view(), name="add_name_type"),
    path('edit_name_type/<str:slug>', EditCscNameTypeView.as_view(), name="edit_name_type"),
    path('delete_name_type/<str:slug>', DeleteCscNameTypeView.as_view(), name="delete_name_type"),
    # Pop up box urls end    
    ]
