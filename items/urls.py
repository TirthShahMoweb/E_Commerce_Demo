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
    path("login/",views.login,name='user_login'),
    path('logout_user/',views.logout_user,name='logout_user'),
    path('signup/',views.signup_update,name='user_signup'),
    path('user_profile/',views.user_profile,name='user_profile'),
    
    #Add to Cart, View Cart,  
    path('add_to_cart/<slug:product_slug>/',views.add_to_cart,name='add-to-cart'),
    path('cart_order/',views.cart_order,name='cart_order'),
    path('product_order/<slug:product_slug>/', views.order, name='product_order'),
    path('show-cart/',views.show_cart,name='show_cart'),

    path('desc_value/product-details/<slug:product_slug>', views.desc_value, name='decrease'),
    path('desc_value/cart/<slug:product_slug>', views.desc_value_cart, name='decrease_cart'),
    path('inc_value/product-details/<slug:product_slug>', views.inc_value, name='increase'),
    path('inc_value/cart/<slug:product_slug>', views.inc_value_cart, name='increase_cart'),

    path('add_address/',views.add_address, name="add_address")
    
    # path('test-404/', lambda request: HttpResponseNotFound())
    ]