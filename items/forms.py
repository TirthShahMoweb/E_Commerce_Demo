from django import forms
from .models import Product,User

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_price', 'product_quantity', 'product_rating', 'product_company_name', 'product_info']

    # Customizing the widgets
    product_name = forms.CharField(
        label='Product Name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    product_price = forms.DecimalField(
        label='Product Price',
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    product_quantity = forms.IntegerField(
        label='Product Quantity',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    product_rating = forms.DecimalField(
        label='Product Rating (0 to 5)',
        max_digits=2,
        decimal_places=1,
        min_value=0,
        max_value=5,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    product_company_name = forms.CharField(
        label='Product Company Name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    product_info = forms.CharField(
        label='Product Info',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )


class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['user_username','user_name','user_email','user_mobile','user_password','user_age' ,'user_role','user_image']
    
    user_username = forms.CharField(
    max_length=18,
    label="Username",
    required=True,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your username',
        'name': 'username'  # Add the name attribute here
    }),
)

    user_name = forms.CharField(
        max_length=50,
        label="Full Name",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name' }),
    )
    user_email = forms.EmailField(
        label="Email Address",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
    )
    user_mobile = forms.CharField(
        max_length=10,
        label="Mobile Number",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your 10-digit mobile number'}),
    )
    user_password = forms.CharField(
        max_length=50,
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter a strong password','name': 'password'}),
    )
    user_age = forms.IntegerField(
        label="Age",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter your age'}),
    )
    ROLE_CHOICES = [
        ('Customer', 'Customer'),
        ('Administrator', 'Administrator'),
    ]

    user_role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="User Role",
        required=True
    )

    user_image = forms.ImageField(
        label="Profile Photo",
        required=False,  # Optional to allow users to skip this
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),  # Allows only image uploads
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Check if instance exists
            self.fields.pop('user_password', None)
            self.fields.pop('user_image',None)