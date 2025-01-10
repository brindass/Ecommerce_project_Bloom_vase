from django.contrib import admin
from .models import *
# Register your models here.

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    fields = ['color', 'quantity', 'variant_image']
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','category', 'price', 'soft_deleted']
    inlines = [ProductVariantInline]



admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(ProductImage)
