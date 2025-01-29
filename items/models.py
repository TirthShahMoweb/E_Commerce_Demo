from django.utils.text import slugify
from django.db import models
from django.core.validators import RegexValidator,MinLengthValidator
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, m2m_changed
from django.dispatch import receiver

import os
import uuid
from ecommerce.settings import MEDIA_ROOT

class Product(models.Model):
    product_name = models.CharField(max_length=100,unique=True)
    product_price = models.IntegerField()
    product_quantity = models.IntegerField()
    product_rating = models.FloatField()
    product_company_name = models.CharField(max_length=50)
    product_info = models.CharField(max_length=2000,null=True)
    product_slug = models.SlugField(max_length=100, unique=True, blank=True)
    product_del = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.product_slug:
            self.product_slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

@receiver(pre_save, sender=Product)
def create_product_slug(sender, instance, **kwargs):
    if not instance.product_slug:
        instance.product_slug = slugify(instance.product_name)

def unique_profile_pic_path(instance, filename):
    ext = os.path.splitext(filename)[1]  # e.g., .jpg or .png
    unique_filename = f"{uuid.uuid4()}{ext}"
    # Return the full upload path
    return os.path.join("profile_pics/", unique_filename)

class User(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    user_username = models.CharField(max_length=18,primary_key=True,validators=[
                    RegexValidator(regex=r'^[a-zA-Z0-9_]+$',
                    message='Username can only contain letters, numbers, and underscores.',
                    code='invalid_username')])
    user_name = models.CharField(max_length=50)
    user_email = models.EmailField()
    user_mobile = models.IntegerField()
    user_password = models.CharField(max_length=50,validators=[MinLengthValidator(8,message="Field must be at least 5 characters long."),
                    RegexValidator(regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$',
                    message=("Password must contain at least 8 characters, "
                    "including one uppercase letter, one number, and one special character."))])
    user_gender = models.CharField(max_length=1, choices=GenderChoices.choices)
    user_age = models.IntegerField()
    user_role = models.CharField(max_length=25)
    user_order = models.JSONField(null=True)
    user_cart = models.JSONField(null=True)
    user_image = models.ImageField(upload_to=unique_profile_pic_path, null=True, blank=True)
    user_address = models.JSONField(null=True,blank=True)
    user_wishlist = models.ManyToManyField(Product, related_name='user_wishlist_User', blank=True)

    def save(self,*args,**kargs):
        super(User,self).save(*args,**kargs)

@receiver(pre_delete, sender=User)
def pre_delete_img(sender,instance, **kwargs):
    if instance.user_image:
        img_path=os.path.join(MEDIA_ROOT,str(instance.user_image))
        if os.path.exists(img_path):
            os.remove(img_path)

@receiver(post_delete, sender=User)
def post_delete_msg(sender, instance, **kwargs):
    print("Thank you for visiting!",{instance.user_name})

@receiver(pre_save, sender=User)
def pre_save_receiver(sender, instance, **kwargs):
    instance.user_address = []

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders', to_field='user_username')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_order')
    order_date = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=1)


@receiver(m2m_changed, sender=User.user_wishlist.through)
def wishlist_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Handles changes in the User's wishlist (ManyToManyField).
    """
    if action == "pre_add":
        print(f"Wishlist: Products about to be added: {pk_set} for user {instance.user_username}")
    elif action == "post_add":
        print(f"Wishlist: Products added: {pk_set} for user {instance.user_username}")
    elif action == "pre_remove":
        print(f"Wishlist: Products about to be removed: {pk_set} for user {instance.user_username}")
    elif action == "post_remove":
        print(f"Wishlist: Products removed: {pk_set} for user {instance.user_username}")
    elif action == "pre_clear":
        print(f"Wishlist: All products about to be cleared for user {instance.user_username}")
    elif action == "post_clear":
        print(f"Wishlist: All products cleared for user {instance.user_username}")