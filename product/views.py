from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Product, ProductImage, Category

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


def product_list_search(request):
    print("inside search")
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort_by')
    search_query = request.GET.get('query', '')

    products = Product.objects.filter(soft_deleted=False)

  
    if search_query:
        products = products.filter(name__icontains=search_query).exclude(soft_deleted = True,category__inactive = True)


    if category_id:
        products = products.filter(category_id=category_id).exclude(soft_deleted = True,category__inactive = True)

    
    if sort_by == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-price')
    elif sort_by == 'new_arrivals':
        products = products.order_by('-created')
    elif sort_by == 'alphabetical_az':
        products = products.order_by('name')
    elif sort_by == 'alphabetical_za':
        products = products.order_by('-name')

    
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    categories = Category.objects.filter(inactive=False)
    
    context = {
        'products': page,
        'categories': categories,
        'selected_category': category_id,
        'selected_sort_by': sort_by,
        'search_query': search_query,
    }

    return render(request,'product_list_search.html', context)

