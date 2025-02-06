from django import forms
from .models import Coupon


class AddCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['coupon_code', 'coupon_name', 'discount_percentage', 'min_purchase_amount', 'is_active']

class EditCouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = '__all__'
        exclude = ['created_at']