from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, User
from .forms import ProductForm, UserForm
from django.utils.text import slugify
# from django.views.generic.base import RedirectView


def show_product(request):
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
    else:
        user=None
    all_companies_name = Product.objects.values('product_company_name').distinct()
    all_products = Product.objects.all()
    logged_user = request.session.get('logged_user')  # Retrieve logged user from session
    return render(request, "items/show_products.html", {
        'user' : user,
        'products': all_products,
        'company': all_companies_name,
        'logged_user': logged_user
    })

def add_or_update_product(request, product_slug=None):
    item_names = Product.objects.values_list('product_name', flat=True)
    if product_slug:
        product = get_object_or_404(Product, product_slug=product_slug)
        old_product_name = product.product_name
    else:
        product = None  # No product to update, so we're adding a new one

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()  # Save the new or updated product
            if product is not None and old_product_name != product.product_name:
                product.product_slug = slugify(product.product_name)
                product.save()
            return redirect('show_product')
    else:
        form = ProductForm(instance=product)  # Populate form with existing product if updating

    return render(request, 'items/product_update.html', {'form': form, 'item_names': item_names})

def product_details(request, product_slug):
    identified_product = list(Product.objects.filter(product_slug=product_slug).values())
    if 'quantity' not in request.session:
        request.session['quantity']=1
    if 'product_slug' in request.session:
        if product_slug!=request.session['product_slug']:
            del request.session['product_slug']
            del request.session['quantity']
            request.session['product_slug']=product_slug
            request.session['quantity']=1
    else:
        request.session['product_slug']=product_slug
    return render(request, "items/product_details.html", {'product': identified_product[0],'quantity':request.session['quantity']})

def product_delete(product_slug):
    del_product = Product.objects.filter(product_slug=product_slug)
    del_product.delete()
    return redirect('show_product')

def search_products(request):
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
    else:
        user=None
    search_data = request.GET.get("query")
    all_companies_name = Product.objects.values('product_company_name').distinct()
    products = Product.objects.all()
    if search_data:
        products = products.filter(product_name__icontains=search_data)
    return render(request, "items/searched_product.html", {
        'user' : user,
        'products': products,
        'query': search_data,
        'company': all_companies_name
    })

def filter_sort(request):
    filter_data = request.GET.get("filter")
    selected_company_data = request.GET.get("companies")
    search_data = request.GET.get("query")
    all_companies_name = Product.objects.values('product_company_name').distinct()
    products = Product.objects.all()
    if search_data:
        products = products.filter(product_name__icontains=search_data)
    if selected_company_data:
        products = products.filter(product_company_name=selected_company_data)
    if filter_data == "price_asc":
        products = products.order_by("product_price")
    elif filter_data == "price_desc":
        products = products.order_by("-product_price")
    elif filter_data == "rating_high":
        products = products.order_by("product_rating")
    elif filter_data == "rating_low":
        products = products.order_by("-product_rating")
    return render(request, 'items/searched_product.html', {
        'products': products,
        'query': search_data,
        'company': all_companies_name
    })

def login(request):
    msg = None
    if request.method == "GET":
        user_name = request.GET.get("username")
        user_pwd = request.GET.get("password")
        user = User.objects.filter(user_username=user_name).first()
        if user and user.user_password == user_pwd:  # Check credentials
            request.session['logged_user'] = user_name
            if 'cart' in request.session:
                cart=request.session['cart']
                user.user_cart=cart
                user.save()
                del request.session['cart']
            return redirect('show_product')
        else:
            msg = "Invalid username or password"
    return render(request, 'items/login.html', {'messages': [msg],'logged_user':user_name})

def logout_user(request):
    del request.session['logged_user']
    return redirect("show_product")

def signup_update(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST,request.FILES)
        if user_form.is_valid():
            user = user_form.save()
            if 'user_Image' in request.FILES:
                user.user_image = request.FILES['user_Image']
            request.session['logged_user'] = user.user_username  # Store user in session
            
            if 'cart'in request.session:
                user=User.objects.filter(user_username=request.session['logged_user']).first()
                if user.user_cart is None:
                    user.user_cart=request.session['cart']
                user.save()
            return redirect('show_product')
    else:
        user_form = UserForm()
    return render(request, 'items/signup.html', {'user_form': user_form})

def add_to_cart(request, product_slug):
    product = Product.objects.filter(product_slug=product_slug).values().first()
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        cart=user.user_cart
        if cart==None:
            cart={}
    else:
        if 'cart' not in request.session:
            cart={}
        else: 
            cart = request.session['cart']

    if str(product['id']) not in cart:
        cart[str(product['id'])] = request.session['quantity']
        del request.session['quantity']
    else:
        cart[str(product['id'])] += request.session['quantity']
        print(cart)
        del request.session['quantity']
    if 'logged_user' in request.session:
            user.user_cart=cart
            user.save()
    request.session['cart'] = cart
    return redirect("show_product")

def show_cart(request):
    total_value=0
    logged_user = request.session.get('logged_user')
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        cart=User.objects.filter(user_username=request.session['logged_user']).values_list('user_cart', flat=True).first()
        if cart is not None:
            logged_user_cart=Product.objects.filter(id__in=cart)
            price=Product.objects.filter(id__in=cart).values('product_price','id')
            for i in price:
                total_value+=cart[str(i['id'])]*i['product_price']
        else:
            logged_user_cart=None
    else:
        user=None
        if 'cart' in request.session:
            logged_user_cart=Product.objects.filter(id__in=request.session['cart'])
            price=Product.objects.filter(id__in=request.session['cart']).values('product_price','id')
            total_value=0
            cart=request.session['cart']
            for i in price:
                total_value+=cart[str(i['id'])]*i['product_price']        
        else:
            cart=None
            total_value=0
            logged_user_cart=None
    return render(request, 'items/show-cart.html', {'cart':cart,'products': logged_user_cart,'user':user,'total_value':total_value,'logged_user':logged_user})

def user_profile(request):
    if 'logged_user' in request.session:
        user_data = request.session['logged_user']
        logged_user=User.objects.filter(user_username=user_data)
    else:
        return redirect('user_login')
    return render(request,'items/user_profile.html',{'logged_user':logged_user})

def order(request,product_slug):
    if 'logged_user' in request.session:
        product=Product.objects.filter(product_slug=product_slug).first()
        # product.product_quantity-=1
        # product.save()
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        msg="Order has been Successfully Placed"
        return render(request,'items/product_order.html',{'product':product,'message':msg,'user':user})
    else:
        return redirect('user_login')

def cart_order(request):
    msg="Order has been Successfully Placed"
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        product=Product.objects.filter(id__in=(user.user_cart)).values()
        print(user)
        total_price=0
        for i in product:
            total_price+=user.user_cart[str(i['id'])]*i['product_price']
        if user.user_order is None:
            user.user_order=user.user_cart
        else:
            
            for i in user.user_cart:
                if i not in user.user_order:
                    user.user_order[i] = user.user_cart[i]
                else:
                    user.user_order[i] += user.user_cart[i]
            user.user_cart={}
        user.save()
        return render(request,'items/order_cart.html',{'user':user,"message":msg,'product':product,'total_price':total_price})
    else:
        return redirect('user_login')

def desc_value(request,product_slug):
    request.session['product_slug'] = product_slug
    if 'quantity' not in request.session:
        request.session['quantity'] = 1
    else:
        request.session['quantity'] -= 1
    return redirect('product_detail', product_slug=product_slug)

def desc_value_cart(request,product_slug):
    product_id = Product.objects.filter(product_slug=product_slug).values_list(flat=True).first()
    
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        cart=user.user_cart
    else:
        cart=request.session['cart']
        
    cart[str(product_id)] -= 1

    if cart[str(product_id)]==0:
        cart.pop(str(product_id))
    
    if 'logged_user' in request.session:
        user.user_cart=cart
        user.save()
    else:
        request.session['cart']=cart
    
    return redirect('show_cart')

def inc_value_cart(request,product_slug):
    product_id = Product.objects.filter(product_slug=product_slug).values_list(flat=True).first()
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        cart=user.user_cart
    else:
        cart=request.session['cart']
    cart[str(product_id)] += 1
    
    if 'logged_user' in request.session:
        user.user_cart=cart
        user.save()
    else:    
        request.session['cart']=cart
    return redirect('show_cart')

def inc_value(request, product_slug):
    request.session['product_slug'] = product_slug
    if 'quantity' not in request.session:
        request.session['quantity'] = 2
    else:
        request.session['quantity'] += 1
    return redirect('product_detail', product_slug=product_slug)
  
def add_address(request):
    if request.method == "POST":
        address=request.POST.get("user_address")
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        if user.user_address is None:
            user.user_address=[address]
        else:
            user.user_address=(user.user_address).append(address)
        user.save()
        print(user,"---------------------------------")
    return redirect("cart_order")


# def error_404(request,exception=None):
    # return render(request, '404.html',  status=404)

# class DescValueRedirectView(RedirectView):
#     permanent = False

#     def get_redirect_url(self, *args, **kwargs):
#         product_slug = kwargs.get('product_slug')
#         self.request.session['product_slug'] = product_slug

#         if 'quantity' not in self.request.session:
#             self.request.session['quantity'] = 1
#         else:
#             self.request.session['quantity'] -= 1

#         return super().get_redirect_url(*args, **kwargs)
