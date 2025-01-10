from django import forms
from .models import Product, ProductVariant
from django.forms import inlineformset_factory

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'base_image', 'quantity', 'price', 'description', 'discount', 'size', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'base_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter product quantity'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter product price'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter product description'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount amount'}),
            'size': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Enter product size'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            # 'parent_product': forms.Select(attrs={'class': 'form-control'}),
            # 'color': forms.TextInput(attrs={'class': 'form-control'}),
        }
class ProductVariantForm(forms.ModelForm):

    class Meta:
        model = ProductVariant
        fields = ['product','color','quantity', 'variant_image']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True
)
        