from django import forms
from .models import Product, ProductVariant, CategoryOffer, ProductOffer
from django.forms import inlineformset_factory, BaseInlineFormSet, ValidationError


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'base_image', 'price', 'description', 'discount', 'size', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'base_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            # 'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter product quantity'}),
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
        fields = ['color', 'quantity', 'variant_image', 'is_default']
        widgets = {
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter color'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter quantity'}),
            'variant_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomProductVariantFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        
        # Count non-deleted forms
        valid_forms = [form for form in self.forms 
                      if form.cleaned_data and not form.cleaned_data.get('DELETE', False)]
        
        # Check if at least one variant exists
        if len(valid_forms) == 0:
            raise ValidationError("At least one variant is required.")
        
        # Check for default variant
        default_variants = [form for form in valid_forms 
                          if form.cleaned_data.get('is_default', False)]
        
        if len(default_variants) == 0:
            raise ValidationError("At least one variant must be marked as default.")
        elif len(default_variants) > 1:
            raise ValidationError("Only one variant can be marked as default.")

ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    formset=CustomProductVariantFormSet,
    extra=1,
    can_delete=True,
    validate_min=1
)

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['name','category', 'discount_percentage', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}), 
            'category': forms.Select(attrs={'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

class EditCategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['name','category', 'discount_percentage', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['product', 'discount_percentage', 'start_date', 'end_date']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }       

class EditProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['product', 'discount_percentage', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
