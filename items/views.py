from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, User, Order
from .forms import ProductForm, UserForm
from django.utils.text import slugify
from datetime import datetime
from django.core.mail import send_mail
from ecommerce import settings
import random


def show_product(request):
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
    else:
        user=None
    
    all_companies_name = Product.objects.values('product_company_name').distinct()
    all_products = Product.objects.filter(product_del=False)
    logged_user = request.session.get('logged_user')  # Retrieve logged user from session
    return render(request, "items/show_products.html", {
        'user' : user,
        'products': all_products,
        'company': all_companies_name,
        'logged_user': logged_user
    })

def add_or_update_product(request, product_slug=None):
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

    return render(request, 'items/product_update.html', {'form': form})

def product_details(request, product_slug):
    identified_product = list(Product.objects.filter(product_slug=product_slug).values())
    if 'quantity' not in request.session:
        if identified_product[0]['product_quantity']==0:
            request.session['quantity']=0
        else:
            request.session['quantity']=1
    
    if 'product_slug' in request.session:
        if product_slug!=request.session['product_slug']:
            del request.session['product_slug']
            del request.session['quantity']
            request.session['product_slug']=product_slug
            if identified_product[0]['product_quantity']==0:
                request.session['quantity']=0
            else:
                request.session['quantity']=1
    else:
        request.session['product_slug']=product_slug
    
    user_role=None
    if 'logged_user' in request.session:
        user_role=User.objects.filter(user_username=request.session['logged_user']).values_list('user_role').first()
        user_role=user_role[0]
    return render(request, "items/product_details.html", {'product': identified_product[0],'quantity':request.session['quantity'],'user_role':user_role})

def product_delete(request,product_slug):
    del_product = Product.objects.filter(product_slug=product_slug).first()
    del_product.product_del=True
    del_product.save()
    # del_product.delete()  
    return redirect('show_product')

def search_products(request):
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
    else:
        user=None
    
    search_data = request.GET.get("query")
    all_companies_name = Product.objects.values('product_company_name').distinct()
    products = Product.objects.filter(product_del=False)
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
    products = Product.objects.filter(product_del=False)
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
    user_name=None
    if request.method == "POST":
        user_name = request.POST.get("username")
        user_pwd = request.POST.get("password")
        user = User.objects.filter(user_username=user_name).first()
        if user:  # Check credentials
            request.session['check_user'] = user_name
            send_otp(request)
            return redirect('valid_otp')
        else:
            msg = "Invalid username or password"
    return render(request, 'items/login.html', {'messages': [msg],'logged_user':user_name})

def logout_user(request):
    del request.session['logged_user']
    return redirect("show_product")

def send_email(subject,message,user_email):
    send_mail(
        subject,message,settings.EMAIL_HOST_USER,user_email)

def send_otp(request):
    user = User.objects.filter(user_username=request.session['check_user']).first()
    otp = generate_OTP()
    request.session['otp'] = otp
    subject = "Your One-Time Password (OTP) for Login"
    message = f'''Dear {user.user_name},

We received a request to log in to your account on E-commerce Demo. To proceed, please use the following One-Time Password (OTP):

{otp}

If you did not request this login attempt, please disregard this email or contact our support team immediately.

For your security, do not share this OTP with anyone. Our team will never ask you for your password or OTP.

If you need assistance, feel free to reach us.
'''
    send_email(subject,message,[user.user_email])

def resend_otp(request):
    send_otp(request)
    return render(request,'items/otp.html')

def change_password(request,user_username):
    msg=None
    if request.method=='POST':
        current_password = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm_new_pass = request.POST.get('confirm_password')
        # user=request.session['logged_user']
        old_pass = User.objects.filter(user_username=user_username).first()
        if old_pass.user_password == current_password and new_pass==confirm_new_pass:
            old_pass.user_password=confirm_new_pass
            old_pass.save()
            return redirect('show_product')
        elif old_pass.user_password != current_password :
            msg='Current password is incorrect.'
        elif new_pass!=confirm_new_pass:
            msg='New password and Confirm password are not same.'
    return render(request, 'items/change_password.html', {'msg': msg, 'user_username': user_username})

def mail_password_change(request,user_username):
    user=User.objects.filter(user_username=user_username).first()
    link=f'http://127.0.0.1:8000/change_pass/{user_username}/'
    subject='Password Change Request'
    message = f'''Dear {user.user_name},

We received a request to change the password for your account. To proceed, please click the link below:

{link}

If you did not request a password change, please ignore this email or contact our support team if you have any concerns.

For security reasons, this link will expire in [expiration time, e.g., 24 hours].

Thank you,  
E-commerce Demo Support Team'''
    send_email(subject,message,[user.user_email])
    return redirect('show_product')

def valid_otp(request):   
    if request.method=='POST':
        entered_otp = int(request.POST.get("otp"))
        session_otp = request.session.get("otp")
        if entered_otp==session_otp:
            user = request.session['check_user']
            request.session['logged_user'] = user
            del request.session['check_user']
            if 'cart' in request.session:
                cart=request.session['cart']
                user.user_cart=cart
                user.save()
                del request.session['cart']
            return redirect('show_product')
        else:
            msg="Invalid OTP"
            return render(request,'items/otp.html')
    return render(request, 'items/otp.html')

def generate_OTP():
    random_number = random.randint(1000, 9999)
    return random_number

def signup_update(request,user_username=None):
    if user_username:
        user=get_object_or_404(User, user_username=user_username)
    else:
        user=None
    if request.method == 'POST':
        user_form = UserForm(request.POST,request.FILES, instance=user)
        if user_form.is_valid():
            user = user_form.save()              
            request.session['logged_user'] = user.user_username  # Store user in session 
            if 'cart'in request.session:
                user=User.objects.filter(user_username=request.session['logged_user']).first()
                if user.user_cart is None:
                    user.user_cart=request.session['cart']
                user.save()
            
            subject="Welcome to E-commerce Demo - We're Thrilled to Have You!"
            message=f"Dear {user.user_name},\n Welcome to E-commerce Demo! We're thrilled to have you join our growing community of shoppers who love discovering incredible deals, exclusive products, and a seamless online shopping experience."
            send_email(subject,message,[user.user_email])
            return redirect('show_product')
    else:
        user_form = UserForm(instance=user)
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
        del request.session['quantity']
    if 'logged_user' in request.session:
            user.user_cart=cart
            user.save()
    request.session['cart'] = cart
    return redirect("show_product")

def show_cart(request):
    total_value = 0
    logged_user = request.session.get('logged_user')
    if 'logged_user' in request.session:
        user = User.objects.filter(user_username=request.session['logged_user']).first()
        cart = User.objects.filter(user_username=request.session['logged_user']).values_list('user_cart', flat=True).first()
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
        product = Product.objects.filter(product_slug=product_slug).first()
        user_username = request.session['logged_user']
        quantity = int(request.session.get('quantity'))
        user_order = Order(user_id=user_username, product=product, quantity=quantity)
        user_order.save()
        product.product_quantity -= quantity
        product.save()
        del request.session['quantity']
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        msg = "Order has been successfully placed"
        return render(
            request,
            'items/product_order.html',
            {'product': product, 'message': msg, 'user': user, 'quantity': quantity}
        )
    else:
        return redirect('user_login')

def cart_order(request):
    msg="Order has been Successfully Placed"
    if 'logged_user' in request.session:
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        product=Product.objects.filter(id__in=(user.user_cart)).values()
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

def inc_value(request, product_slug):
    request.session['product_slug'] = product_slug
    if 'quantity' not in request.session:
        request.session['quantity'] = 2
    else:
        request.session['quantity'] += 1
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

def see_order(request,user_username):
    if request.method=='GET':
        start_date=request.GET.get('start_date')
        end_date=request.GET.get('end_date')
    users = User.objects.get(user_username=user_username)
    if start_date and end_date:
        user_orders = users.user_orders.filter(order_date__range=[start_date,end_date])
    else:
        user_orders = users.user_orders.all()
    return render(request,'items/display_orders.html',{'user_orders':user_orders})

def inc_value_cart(request,product_slug):
    product_id = Product.objects.filter(product_slug=product_slug).values_list(flat=True).first()
    if 'logged_user' in request.session:
        user = User.objects.filter(user_username=request.session['logged_user']).first()
        cart = user.user_cart
    else:
        cart = request.session['cart']
    cart[str(product_id)] += 1
    
    if 'logged_user' in request.session:
        user.user_cart=cart
        user.save()
    else:    
        request.session['cart']=cart
    return redirect('show_cart')

def add_address(request):
    if request.method == "POST":
        address=request.POST.get("user_address")
        user=User.objects.filter(user_username=request.session['logged_user']).first()
        if user.user_address is None:
            user.user_address=[address]
        else:
            user.user_address=(user.user_address).append(address)
        user.save()
    return redirect("cart_order")

def del_account(request,user_username):
    del request.session['logged_user']
    user=User.objects.filter(user_username=user_username)
    user.delete()
    return redirect("show_product")

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
