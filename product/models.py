from django.db import models
from datetime import datetime

# Create your models here.
class Product(models.Model):
    CHOICES = [
        ('large','Large'),
        ('medium','Medium'),
        ('small','Small')
    ]
    
    name = models.CharField(max_length=100)
    base_image = models.ImageField(upload_to='products/base')
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    description = models.TextField()
    # rating = models.PositiveIntegerField(default=1) # max upto 5
    
    created = models.DateTimeField(default=datetime.now)
    discount = models.FloatField()
    size = models.CharField(max_length=20,choices=CHOICES,default = 'small')
    category = models.ForeignKey('Category',on_delete=models.CASCADE)
    soft_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, null=False)
    inactive = models.BooleanField(default=False) # soft_delete

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/')
    product = models.ForeignKey('Product',on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name
    
class Product_reviews(models.Model):
    user = models.ForeignKey('user.MyUser',on_delete=models.CASCADE)
    product = models.ForeignKey('Product',on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f"{self.user.name} {self.product.name}"
    