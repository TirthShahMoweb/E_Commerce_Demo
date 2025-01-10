from django.utils.text import slugify
from django.db import models
from django.core.validators import RegexValidator,MinLengthValidator
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
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

class User(models.Model):
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
    user_age = models.IntegerField()
    user_role = models.CharField(max_length=25)
    user_order = models.JSONField(null=True)
    user_cart = models.JSONField(null=True)
    user_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    user_address = models.JSONField(null=True,blank=True)
    # user_del = models.BooleanField(default=False)
    
    def save(self,*args,**kargs):
        super(User,self).save(*args,**kargs)
    
@receiver(pre_save, sender=User)
def post_save_receiver(sender, instance, **kwargs):
    instance.user_address = []