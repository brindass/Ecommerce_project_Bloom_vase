from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product, ProductImage

# Create your views here.

def list_product(request):
    # print("inside list product")
    new_arrivals = Product.objects.all().order_by('-created')[:3]
    products = Product.objects.filter(soft_deleted=False)
    paginator = Paginator(products,9)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'products':page,
        'new_arrivals':new_arrivals
    }
    # print("The product details ",page)
    return render(request,'product/home.html',context)

def test(request):
    return render(request,'product/test.html')

def product_details(request,pk):
    product = Product.objects.get(id=pk)
    images = ProductImage.objects.filter(product = product)
    context = {'product':product,
               'images':images}
    print(images,product)
    return render(request,'product/product_details.html',context)




