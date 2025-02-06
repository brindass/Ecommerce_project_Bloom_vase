from django.db import models
from user.models import MyUser,Address
from product.models import Product
from django.utils import timezone
from my_admin.models import Coupon


# Create your models here.

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending','Pending'),
        ('Processing','Processing'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled')

    )
    
    RETURN_STATUS_CHOICES = (
        ('Return Requested','Return Requested'),
        ('Returned','Returned'),
        ('Rejected','Rejected')
    )

    PAYMENT_STATUS_CHOICES = (
        ('Pending','Pending'),
        ('Paid','Paid')

    )

    user = models.ForeignKey(MyUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    street_address=models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20)
    payment = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=100,choices=PAYMENT_STATUS_CHOICES,default='Pending')
    is_return = models.BooleanField(default=False)
    return_status = models.CharField(max_length=100,choices = RETURN_STATUS_CHOICES,default='none')
    is_cancelled = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    variant = models.ForeignKey('product.ProductVariant', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"OrderItem:{self.product.name}"
    

class OrderCancellation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='cancellations')
    reason = models.TextField()
    cancel_status = models.CharField(max_length=10, choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')], default = 'pending')
    cancelled_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cancellation of Order {self.order.id} by {self.order.user.email}"

    
class ReturnReason(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
