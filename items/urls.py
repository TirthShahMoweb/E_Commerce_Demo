# from django.http import HttpResponseNotFound
from django.urls import path
from . import views

urlpatterns = [
    # Crud for Products and home Page
    path("add_products/",views.add_or_update_product,name="add_product"),
    path("delete_product/<slug:product_slug>/",views.product_delete,name='product_delete'),
    path("products/",views.show_product,name="show_product"),
    path('products/<slug:product_slug>/', views.product_details, name='product_detail'),
    path("product_update/<slug:product_slug>/",views.add_or_update_product,name="product_update"),
    
    #Serach ad Sort
    path("search/",views.search_products,name="search_items"),
    path("search/filter-sort",views.filter_sort,name="filter_sort"),
    
    # User Crud
    path("change_pass/<str:user_username>/",views.change_password,name="change_pass"),
    path("delete_account/<str:user_username>/",views.del_account,name="del_account"),
    path("login/",views.login,name='user_login'),
    path('login/otp/',views.valid_otp,name='valid_otp'),
    path('login/resend_otp/',views.resend_otp,name='resend_otp'),
    path('logout_user/',views.logout_user,name='logout_user'),
    path("send_email/<str:user_username>/",views.mail_password_change,name="send_mail"),
    path('signup/',views.signup_update,name='user_signup'),
    path("user_update/<str:user_username>/",views.signup_update,name="update_user"),
    path('user_profile/',views.user_profile,name='user_profile'),
    
    #Add to Cart, View Cart,  
    path('add_to_cart/<slug:product_slug>/',views.add_to_cart,name='add-to-cart'),
    path('cart_order/',views.cart_order,name='cart_order'),
    path('product_order/<slug:product_slug>/', views.order, name='product_order'),
    path('show-cart/',views.show_cart,name='show_cart'),
    path('see_orders/<str:user_username>/',views.see_order,name='see_orders'),
    
    path('desc_value/product-details/<slug:product_slug>', views.desc_value, name='decrease'),
    path('desc_value/cart/<slug:product_slug>', views.desc_value_cart, name='decrease_cart'),
    path('inc_value/product-details/<slug:product_slug>', views.inc_value, name='increase'),
    path('inc_value/cart/<slug:product_slug>', views.inc_value_cart, name='increase_cart'),

    path('add_address/',views.add_address, name="add_address")
    
    # path('test-404/', lambda request: HttpResponseNotFound())
    ]