from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, ProductImage, Category, ProductVariant
from user.models import Wishlist, WishlistItem
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
    product = Product.objects.get(id = pk)
    images = ProductImage.objects.filter(product = product)
    # all_products = []
    variants = product.variants.all() 

    product_in_wishlist = False
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            product_in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, product=product).exists()
    
    
    # variants_images = ProductImage.objects.filter(product__in=product_variants).first()
    # if product_variants:
    #     all_products = [product] + list(product_variants)

    # has_variants = variants.exists()
    print(variants,'variant') 
    # related_products = Product.objects.filter(category=product.category).exclude(pk=pk)
    context = {'product':product,
               
               'images':images,
               'variants': variants,
               'product_in_wishlist': product_in_wishlist,
            #    'variants_images': variants_images,
            #    'related_products': related_products
               'page':"product_page",
               
               }
    # print(images,product,has_variants)
    return render(request,'product/product_details.html',context)



def variant_details(request, variant_id):
    variant = ProductVariant.objects.get(id=variant_id)
    other_variants = ProductVariant.objects.filter(product=variant.product).exclude(id=variant_id)

    context = {
        'variant': variant,
        'other_variants': other_variants,
        'page':"variants_page"
    }
    return render(request, 'product/variant_details.html', context)



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

