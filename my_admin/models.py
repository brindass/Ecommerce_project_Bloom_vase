from django.db import models
from django.utils import timezone
from user.models import MyUser

# Create your models here.

# Coupon Model
class Coupon(models.Model):
    coupon_code = models.CharField(max_length=50, unique=True)
    coupon_name = models.CharField(max_length=100)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.coupon_name
    
class SalesReport(models.Model):
    user_admin = models.ForeignKey(MyUser, on_delete=models.CASCADE)  
    start_date = models.DateTimeField()  
    end_date = models.DateTimeField()  
    total_sales_delivered = models.DecimalField(max_digits=10, decimal_places=2) 
    delivery_order_count = models.IntegerField(default=0)  
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2) 
    total_actual_price = models.DecimalField(max_digits=10, decimal_places=2)  
    total_offer_discount = models.DecimalField(max_digits=10, decimal_places=2)  
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Sales Report ({self.start_date.date()} - {self.end_date.date()})"