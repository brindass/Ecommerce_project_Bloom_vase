from django.db import models
from django.utils import timezone

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