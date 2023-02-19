from django.db import models
from accounts.models import BrandUserProfile, ShopperProfile
from django.utils.text import slugify

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=200, null=False)
    slug = models.SlugField(max_length=200, unique=True, null=False)
    
    brand = models.ForeignKey(BrandUserProfile, on_delete=models.CASCADE)
    
    price = models.IntegerField(blank=False, default=0)
    image = models.ImageField(upload_to='products', null=True, blank=True, max_length=200)
    description = models.TextField(blank=True)
    
    stock = models.IntegerField(default=0, blank=True, null=True)
    is_available = models.BooleanField(default=True) # False if the product not issued anymore (or yet)
    
    class Meta:
        unique_together = (('slug', 'brand'),)
    
    def __str__(self):
        return self.name
    
    def add_to_cart(self, profile, qtt = 1):
        item, created = Item.objects.get_or_create(product=self, buyer=profile, bought=False)
        
        if created:
            item.quantity = qtt
        else:
            item.add_to_cart(qtt)
            item.save()
            
    def remove_from_cart(self, profile):
        try:
            item = Item.objects.get(product = self, buyer = profile, bought = False)
            item.delete()
        except:
            pass
    
    def change_quantity(self, profile, qtt):
        if qtt <= 0:
            self.remove_from_cart(profile)
            return
        try:
            item = Item.objects.get(product = self, buyer = profile, bought = False)
            item.quantity = qtt
            item.save()
        except:
            pass
    
    def create(name, brand):
        if not Product.objects.filter(name = name, brand = brand).exists():
            Product.objects.create(name = name, brand = brand)
            return name
        
        i = 0
        while True:
            if not Product.objects.filter(name = name + '_' + str(i), brand = brand).exists():
                Product.objects.create(name = name + '_' + str(i), brand = brand)
                return name + '_' + str(i)
            i += 1
    
    def update_stock(self, qtt):
        self.stock = qtt
        self.save()
    
    def deactivate(self):
        self.is_available = False
        Item.objects.filter(product = self).delete()
        self.save()
    
    def activate(self):
        self.is_available = True
        self.save()
    
    @property
    def brand_name(self):
        return self.brand.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
        

class Command(models.Model):
    address = models.CharField(max_length=1024)
    sent = models.BooleanField(default=False)
    arrived = models.BooleanField(default=False)
    payment_session = models.CharField(max_length=250, null=True, blank=True, default=None)
    payed = models.BooleanField(default=False)
    
    @property
    def items(self):
        return Item.objects.filter(command = self)
    
    @property
    def price(self):
        return sum([item.price for item in self.items])
    
    def cancel(self):
        for item in self.items:
            if item.product.stock != None:
                item.product.update_stock(item.product.stock + item.quantity)
        self.delete()

class Item(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    buyer = models.ForeignKey(ShopperProfile, on_delete=models.CASCADE)
    bought = models.BooleanField(default=False) # If false then the product is in cart
    
    data_time = models.DateTimeField(null=True, blank=True)
    command = models.ForeignKey(Command, default=None, null=True, blank=True, on_delete=models.SET_DEFAULT)
    price_on_buying = models.IntegerField(default=None, null=True, blank=True) #Can be fixed but not bought if order is canceled
        
    
    def __str__(self):
        return self.product.name

    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    def add_to_cart(self, qtt = 1):
        self.quantity += qtt
        self.save()
    
    def set_quantity(self, qtt):
        self.quantity = qtt
        self.save()
    
    @property
    def brand_name(self):
        return self.product.brand_name
    
    def is_cart_empty(profile):
        return not Item.objects.filter(buyer = profile, bought = False).exists()