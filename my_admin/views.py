from django.shortcuts import render
from user.models import MyUser, Wallet, Transaction
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from product.models import Category, Product, CategoryOffer, ProductOffer
from product.forms import ProductForm, ProductVariantFormSet, ProductOfferForm, EditProductOfferForm, CategoryOfferForm, EditCategoryOfferForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from order.models import Order,OrderItem, OrderCancellation
from decimal import Decimal
from datetime import datetime,timedelta
from django.utils import timezone
from .models import Coupon, SalesReport
from .forms import AddCouponForm, EditCouponForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden
from django.db import IntegrityError
import calendar
import io
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models.functions import TruncDate, TruncMonth, TruncYear


# Create your views here.
def test(request):
    return render(request,'my_admin/category.html')

def admin_dashboard(request):
    if request.user.is_staff:
        # Total Sales Count (Delivered Orders)
        total_sales = Order.objects.filter(status='Delivered', is_cancelled=False).count()
        
        # Total Revenue (Sum of total_price for Delivered Orders)
        total_price = Order.objects.filter(status='Delivered', is_cancelled=False).aggregate(total_price=Sum('total_price'))['total_price'] or Decimal(0)

        # Total Users
        total_users = MyUser.objects.count()
        
        # Best Selling Products (Top 10)
        top_products = (
            OrderItem.objects.values('product')
            .annotate(order_count=Count('id'))
            .filter(order__status='Delivered', order__is_cancelled=False)
            .order_by('-order_count')[:10]
        )
        
        top_products_with_details = [
            {'product': get_object_or_404(Product, id=item['product']), 'order_count': item['order_count']}
            for item in top_products
        ]
        
        # Best Selling Categories (Top 10)
        top_categories = (
            OrderItem.objects.values('product__category')
            .annotate(order_count=Count('id'))
            .filter(order__status='Delivered', order__is_cancelled=False)
            .order_by('-order_count')[:10]
        )
        
        top_categories_with_details = [
            {'category': get_object_or_404(Category, id=item['product__category']), 'order_count': item['order_count']}
            for item in top_categories
        ]
        
        # Daily Sales
        daily_sales = (
            Order.objects.filter(status='Delivered', is_cancelled=False)
            .annotate(date_created=TruncDate('created_at'))
            .values('date_created')
            .annotate(total_sales=Sum('total_price'))
            .order_by('-date_created')
        )
        
        # Monthly Sales
        monthly_sales = (
            Order.objects.filter(status='Delivered', is_cancelled=False)
            .annotate(month_created=TruncMonth('created_at'))
            .values('month_created')
            .annotate(total_sales=Sum('total_price'))
            .order_by('-month_created')
        )
        
        # Yearly Sales
        yearly_sales = (
            Order.objects.filter(status='Delivered', is_cancelled=False)
            .annotate(year_created=TruncYear('created_at'))
            .values('year_created')
            .annotate(total_sales=Sum('total_price'))
            .order_by('-year_created')
        )
        
        context = {
            'total_sales': total_sales,
            'total_price': total_price,
            'total_users': total_users,
            'top_products': top_products_with_details,
            'top_categories': top_categories_with_details,
            'daily_sales': daily_sales,
            'monthly_sales': monthly_sales,
            'yearly_sales': yearly_sales,
        }
        
        return render(request, 'my_admin/admin_dashboard.html', context)
    
    return redirect('admin_login')

# admin_login
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None and user.is_staff: 
            print('inside if')
            
            request.session['admin'] = user.email
            login(request, user)
            return redirect('list_users')  
        else:
            messages.error(request, "Invalid credentials or not an admin.")
    
    return render(request, 'my_admin/admin_login.html')


def list_users(request):
    print('inside users list')
    if request.user.is_staff:
        print('inside ssession')
        search_query = request.GET.get('search','')
        if search_query:
            users = MyUser.objects.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query)
                ).exclude(username='admin')
        else:
            users = MyUser.objects.all().exclude(username = 'admin')
        paginator = Paginator(users,12)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)
        context = {'users':page, 'search_query': search_query}
        return render(request,'my_admin/users.html',context)
    return redirect('admin_login')

def block_or_unblock_user(request,pk):
    if request.user.is_staff:
        user = get_object_or_404(MyUser, id=pk)
        user.is_active = not user.is_active
        messages.success(request, f'User {user.email} status changed.')
        user.save()
        return redirect('list_users') 

def add_category(request):
    if request.user.is_staff:
        if request.method == 'POST':
            name = request.POST.get('name').strip()
            if name:
                if Category.objects.filter(name__iexact=name).exists():
                    messages.error(request,"Category already exists")
                else:
                    Category.objects.create(name=name)
                    messages.success(request, "Category added successfully")
        categories = Category.objects.all()
        context = {'categories':categories}
        print(context)
        return render(request,'my_admin/category.html',context)


def update_category(request, pk):
    if request.user.is_staff:
        if request.method == 'POST':
            category = Category.objects.get(id=pk)
            name = request.POST.get('name').strip()
            
            # Check if the name already exists (excluding the current category)
            if Category.objects.filter(name=name).exclude(id=pk).exists():
                messages.error(request, "A category with this name already exists.")
                return redirect('add_category')
            
            # Update the category name
            category.name = name
            try:
                category.save()
                messages.success(request, "Category updated successfully.")
                return redirect('add_category')
            except IntegrityError:
                messages.error(request, "There was an error updating the category.")
                return redirect('add_category')
     

def delete_category(request,pk):
    if request.user.is_staff:
        category = Category.objects.get(id=pk)
        category.inactive = not category.inactive
        category.save()
        return redirect('add_category')




def create_product(request):
    if  not request.user.is_staff:
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductVariantFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            try:
                product = form.save(commit=False)
                product.save()
                formset.instance = product
                formset.save()
                messages.success(request, 'Product created successfully!')
                return JsonResponse({
                    'status': 'success',
                    'message': 'Product created successfully!'
                })
            except Exception as e:
                if product.id:
                    product.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error creating product: {str(e)}',
                    'form_errors': form.errors,
                    'formset_errors': formset.errors
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Please correct the errors below.',
                'form_errors': form.errors,
                'formset_errors': formset.errors
            })
    else:
        form = ProductForm()
        formset = ProductVariantFormSet()

    products = Product.objects.all().prefetch_related('variants')
    context = {
        'form': form,
        'formset': formset,
        'products': products,
    }
    return render(request, 'my_admin/product_list.html', context)



# # def update_product(request,pk):
#     product = Product.objects.get(id=pk)
#     print('this is the data',request.POST)

def update_product(request):
    if request.user.is_staff:
        product_id = request.POST.get('id')
        product = Product.objects.get(id=product_id) if product_id else None
        
        form = ProductForm(instance=product)
        formset = ProductVariantFormSet(instance=product)

        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            formset = ProductVariantFormSet(request.POST, request.FILES, instance=product)

            if form.is_valid() and formset.is_valid():
                product = form.save()
                formset.save()
                return redirect('create&list_product')
            else:
                print("Form Errors: ", form.errors)
                print("Formset Errors: ", formset.errors)

        context = {
            'form': form,
            'formset': formset,
        }
        return redirect('create&list_product')
    

def delete_product(request,pk):
    if request.user.is_staff:
        product = Product.objects.get(id=pk)
        product.soft_deleted = not product.soft_deleted
        product.save()
        return redirect('create&list_product')
    
def manage_variants(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    formset = ProductVariantFormSet(instance=product)

    if request.method == "POST":
        formset = ProductVariantFormSet(request.POST, request.FILES, instance=product)
        if formset.is_valid():
            formset.save(commit=True)
            for form in formset.forms:
                print("Delete field value: ", form.cleaned_data.get("DELETE"))

            return redirect('create&list_product')

    context = {
        'product': product,
        'formset': formset,
    }
    return render(request, 'my_admin/manage_variants.html', context)

def list_order(request):
    if request.user.is_staff:
        search = request.GET.get('q', '')
        print("Search Query: ", search)

        if request.method == "POST":
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('new_status')
            print(f"Order ID: {order_id}, New Status: {new_status}")
            
            try:
                order = Order.objects.get(pk=order_id)
                wallet = get_object_or_404(Wallet,user = order.user)
                
                print("Order User: ", order.user)

                if order.is_return:
                    order.return_status = new_status
                    if new_status == 'Returned':

                        wallet.amount += Decimal(order.total_price)
                        wallet.save()
                       
                        Transaction.objects.create(wallet = wallet,amount = order.total_price,transaction_type = 'credit')

                        order.payment_status = 'cash refunded to your wallet'
                        order.save()

                    order.save()
                elif new_status == 'Delivered':
                    order.payment_status = 'Paid'
                    order.save()

                if new_status == "Cancelled" :
                    print("Order Cancelled")
                    order_items = OrderItem.objects.filter(order=order)
                    for item in order_items: 
                        item.quantity += item.quantity
                        item.save()

                if new_status == "Returned" :
                    print("Order Returned")
                    order_items = OrderItem.objects.filter(order=order)
                    for item in order_items: 
                        item.quantity += item.quantity
                        item.save()

                if not order.is_return:
                    order.status = new_status
                    order.save()

                return JsonResponse({'success': True})
            except Order.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Order does not exist'})

        orders = Order.objects.all().order_by('-created_at')
        if search:
            orders = orders.filter(
                Q(id__icontains=search) |
                Q(user__username__icontains=search) |
                Q(status__icontains=search)
            )
        paginator = Paginator(orders, 10)  
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)

        context = {
            'orders': page,
        }
        return render(request, 'my_admin/order_list.html', context)
    
def order_details(request, order_id):
    # Check if the user is an admin
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not authorized to access this page.")
    

    # Fetch the order and order items
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'my_admin/admin_order_details.html', context)
    
def admin_cancel_update(request):
    if request.user.is_staff:
        pending_cancellations = OrderCancellation.objects.filter(cancel_status='pending').order_by('-updated_at')
        paginator = Paginator(pending_cancellations, 10)
        page_number = request.GET.get('page')
        page = paginator.get_page(page_number)

        context = {
            'pending_cancellations': page,
        }
        return render(request, 'my_admin/admin_cancel_update.html', context)
    return redirect('admin_login')

def cancel_approve(request, pk):
    if request.user.is_staff:
        cancellation = get_object_or_404(OrderCancellation, id=pk)
        order = cancellation.order

        # Update stock for order items
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.quantity += item.quantity
            item.save()

        # Update order and cancellation status
        order.is_cancelled = True
        order.status = 'cancelled'
        order.save()

        if order.payment_status == 'Paid' or 'Completed':
            print('paid')
            wallet = get_object_or_404(Wallet,user = order.user)
            print(wallet)

            wallet.amount += Decimal(order.total_price)
            wallet.save()

            order.payment_status = 'refunded to wallet'
            order.save()

            Transaction.objects.create(wallet = wallet, amount = order.total_price, transaction_type = 'credit')

        cancellation.cancel_status = 'approved'
        cancellation.save()
        messages.success(request, f"Cancellation request for Order #{order.id} has been approved.")
        return redirect('admin_cancel_update')
    return redirect('admin_login')


def cancel_reject(request, pk):
    if request.user.is_staff:
        cancellation = get_object_or_404(OrderCancellation, id=pk)
        order = cancellation.order

        # Update order and cancellation status
        order.status = 'cancel rejected'
        order.is_cancelled = False
        order.save()

        cancellation.cancel_status = 'rejected'
        cancellation.save()
        messages.error(request, f"Cancellation request for Order #{order.id} has been rejected.")
        return redirect('admin_cancel_update')
    return redirect('admin_login')


# ---- offers -----
def add_category_offer(request):
    if request.user.is_staff:
        form = CategoryOfferForm()
        if request.method == 'POST':
            form = CategoryOfferForm(request.POST)
            if form.is_valid():
                discount_percentage = form.cleaned_data['discount_percentage']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                category = form.cleaned_data['category']
                
                
                current_datetime = timezone.now()

                if discount_percentage < 1:
                    form.add_error('discount_percentage', 'Discount percentage should not be less than 1.')

                if discount_percentage > 90:
                    form.add_error('discount_percentage', 'Discount percentage should not be greater than 90.')

                if start_date > end_date:
                    form.add_error('end_date', 'End date should be greater than start date.')

                if CategoryOffer.objects.filter(category=category).exists():
                    form.add_error('category', 'An offer for this category already exists.')

                if start_date.date() < current_datetime.date() :
                    form.add_error('start_date', 'Offer start date cannot be in the past.')


                if form.errors:
                    context = {'form': form}
                    return render(request, 'my_admin/add_category_offer.html', context)

                form.save()
                return redirect('list_category_offers')

        context = {'form': form}
        return render(request, 'my_admin/add_category_offer.html', context)


def list_category_offers(request):
    if request.user.is_staff:
        category_offers = CategoryOffer.objects.all()
        context = {'category_offers': category_offers}
        return render(request, 'my_admin/list_category_offers.html', context)

def edit_category_offer(request, pk):
    if request.user.is_staff:
        category_offer = get_object_or_404(CategoryOffer, id=pk)
        form = EditCategoryOfferForm(instance=category_offer)
        if request.method == 'POST':
            form = EditCategoryOfferForm(request.POST, instance=category_offer)
            if form.is_valid():
                discount_percentage = form.cleaned_data['discount_percentage']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']

                current_datetime = timezone.now()
                
                if discount_percentage < 1:
                    form.add_error('discount_percentage', 'Discount percentage should not be less than 1.')

                if discount_percentage > 90:
                    form.add_error('discount_percentage', 'Discount percentage should not be greater than 90.')

                if start_date > end_date:
                    form.add_error('end_date', 'End date should be greater than start date.')

                if start_date.date() < current_datetime.date() :
                    form.add_error('start_date', 'Offer start date cannot be in the past.')

                if form.errors:
                    context = {'form': form}
                    return render(request, 'my_admin/edit_category_offer.html', context)

                form.save()
                return redirect('list_category_offers')

        context = {'form': form}
        return render(request, 'my_admin/edit_category_offer.html', context)

    
def delete_category_offer(request, pk):
    if request.user.is_staff:
        offer = get_object_or_404(CategoryOffer, id=pk)
        offer.delete()
        return redirect('list_category_offers')

def add_product_offer(request):
    if request.user.is_staff:
        form = ProductOfferForm()
        if request.method == 'POST':
            form = ProductOfferForm(request.POST)
            if form.is_valid():
                discount_percentage = form.cleaned_data['discount_percentage']
                product = form.cleaned_data['product']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']

                current_datetime = timezone.now()

                
                if discount_percentage < 0:
                    form.add_error('discount_percentage', 'Discount percentage should not be less than 0.')

                if discount_percentage > 90:
                    form.add_error('discount_percentage', 'Discount percentage should not be greater than 90.')

                if discount_percentage >= product.price:
                    form.add_error('discount_percentage', 'Discount percentage should not be greater than or equal to the product price.')

                if start_date > end_date:
                    form.add_error('end_date', 'End date should be greater than start date.')

                if start_date.date() < current_datetime.date() :
                    form.add_error('start_date', 'Offer start date cannot be in the past.')

                if form.errors:
                    context = {'form': form}
                    return render(request, 'my_admin/add_product_offer.html', context)

                form.save()
                return redirect('list_product_offers')

        context = {'form': form}
        return render(request, 'my_admin/add_product_offer.html', context)


def list_product_offers(request):
    if request.user.is_staff:
        product_offer = ProductOffer.objects.all()
        context = {'product_offer': product_offer}
        return render(request, 'my_admin/list_product_offers.html', context)

def edit_product_offer(request, pk):
    if request.user.is_staff:
        offer = get_object_or_404(ProductOffer, id=pk)
        form = EditProductOfferForm(instance=offer)
        if request.method == 'POST':
            form = EditProductOfferForm(request.POST, instance=offer)
            if form.is_valid():
                discount_percentage = form.cleaned_data['discount_percentage']
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']

                current_datetime = timezone.now()

                
                if discount_percentage < 0:
                    form.add_error('discount_percentage', 'Discount percentage should not be less than 0.')

                if discount_percentage > 90:
                    form.add_error('discount_percentage', 'Discount percentage should not be greater than 90.')
                

                if start_date > end_date:
                    form.add_error('end_date', 'End date should be greater than start date.')

                if start_date.date() < current_datetime.date() :
                    form.add_error('start_date', 'Offer start date cannot be in the past.')

                

                if form.errors:
                    context = {'form': form}
                    return render(request, 'my_admin/edit_product_offer.html', context)

                form.save()
                return redirect('list_product_offers')

        context = {'form': form}
        return render(request, 'my_admin/edit_product_offer.html', context)

def delete_product_offer(request, pk):
    if request.user.is_staff:
        offer = get_object_or_404(ProductOffer, id=pk)
        offer.delete()
        return redirect('list_product_offers')



# ----- coupon ------ 
def list_coupon(request):
    if request.user.is_staff:
        coupons = Coupon.objects.all()
        context = {'coupons': coupons}
        return render(request, 'my_admin/list_coupon.html', context)
    return redirect('admin_login')

def add_coupon(request):
    if request.user.is_staff:
        if request.method == "POST":
            form = AddCouponForm(request.POST)
            if form.is_valid():
                coupon_code = form.cleaned_data['coupon_code']
                discount = form.cleaned_data['discount_percentage']
                min_purchase_amount = form.cleaned_data['min_purchase_amount']

                if len(coupon_code) < 6:
                    form.add_error('coupon_code', 'Coupon code must be at least 6 characters long.')

                if discount < 1.00:
                    form.add_error('discount_percentage', 'Discount must be greater than 0.')

                if min_purchase_amount < 10.00:
                    form.add_error('min_purchase_amount', 'Minimum purchase amount must be at least 10.')

                if discount >= min_purchase_amount:
                    form.add_error('discount_percentage', 'Discount must be less than the minimum purchase amount.')

                if Coupon.objects.filter(coupon_code=coupon_code).exists():
                    form.add_error('coupon_code', 'This coupon code already exists.')

                if form.errors:
                    return render(request, 'my_admin/add_coupon.html', {'form': form})
                form.save()
                messages.success(request, "Coupon added successfully!")
                return redirect('list_coupon')
        else:
            form = AddCouponForm()
            context = {'form': form}
        return render(request, 'my_admin/add_coupon.html',context)
    return redirect('admin_login')

def edit_coupon(request, pk):
    if request.user.is_staff:
        coupon = get_object_or_404(Coupon, id=pk)
        if request.method == "POST":
            form = EditCouponForm(request.POST, instance=coupon)
            if form.is_valid():
                coupon_code = form.cleaned_data['coupon_code']
                discount = form.cleaned_data['discount_percentage']
                min_purchase_amount = form.cleaned_data['min_purchase_amount']

                if len(coupon_code) < 6:
                    form.add_error('coupon_code', 'Coupon code must be at least 6 characters long.')

                if discount < 1.00:
                    form.add_error('discount_percentage', 'Discount must be greater than 0.')

                if min_purchase_amount < 10.00:
                    form.add_error('min_purchase_amount', 'Minimum purchase amount must be at least 10.')

                if discount >= min_purchase_amount:
                    form.add_error('discount_percentage', 'Discount must be less than the minimum purchase amount.')

                if Coupon.objects.exclude(id=coupon.pk).filter(coupon_code=coupon_code).exists():
                    form.add_error('coupon_code', 'This coupon code already exists.')

                if form.errors:
                    return render(request, 'my_admin/edit_coupon.html', {'form': form})
                form.save()
                messages.success(request, "Coupon updated successfully!")
                return redirect('list_coupon')
        else:
            form = EditCouponForm(instance=coupon)
            context = {'form': form}
        return render(request, 'my_admin/edit_coupon.html', context)
    return redirect('admin_login')

@csrf_exempt
def apply_coupon(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        print('coupon apply')
        try:
            coupon_code = request.POST.get('coupon')
            total_price = request.POST.get('totalprice')
            print(f"Received Coupon: {coupon_code}, Total Price: {total_price}")

            if not coupon_code:
                return JsonResponse({'status': 'error', 'message': 'Coupon code is required'})

            if total_price is None:
                return JsonResponse({'status': 'error', 'message': 'Total price is required'})

            try:
                total_price = Decimal(total_price)  
                coupon = Coupon.objects.get(coupon_code=coupon_code, is_active=True)

                if total_price >= coupon.min_purchase_amount:
                    discount_amount = (coupon.discount_percentage / Decimal(100)) * total_price
                    new_total_price = total_price - discount_amount

                    return JsonResponse({
                        'status': 'success',
                        'coupon_code': coupon.coupon_code,
                        'discount_percentage': coupon.discount_percentage,
                        'discount_amount': round(discount_amount, 2),
                        'new_total_price': round(new_total_price, 2)
                    })
                else:
                    return JsonResponse({'status': 'error', 'message': "Minimum purchase amount not met"})
            
            except Coupon.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': "Invalid coupon code"})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



def delete_coupon(request, pk):
    if 'admin' in request.session:
        coupon = get_object_or_404(Coupon, id=pk)
        coupon.delete()
        messages.success(request, "Coupon deleted successfully!")
        return redirect('list_coupon')
    return redirect('admin_login')

# generate sales_report
def sales_report(request):
    if request.user.is_staff:
        if request.method == 'POST':
            period = request.POST.get('period')
            start_date = end_date = timezone.now()

            if period == 'daily':
                start_date = timezone.now().replace(hour=0, minute=0, second=0)
            elif period == 'weekly':
                start_date = timezone.now() - timedelta(days=timezone.now().weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0)
                end_date = start_date + timedelta(days=7)
            elif period == 'monthly':
                start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0)
                last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]
                end_date = start_date.replace(day=last_day_of_month, hour=23, minute=59, second=59)
            elif period == 'custom':
                start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').replace(hour=0, minute=0, second=0)
                end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').replace(hour=23, minute=59, second=59)

            delivered_orders = Order.objects.filter(
                created_at__range=[start_date, end_date], status='Delivered'
            ).filter(Q(is_return=False) | Q(return_status='Rejected'))

            total_sales_delivered = delivered_orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
            delivery_order_count = delivered_orders.count()

            # Calculate coupon discount
            coupon_discount = sum(
                (order.total_price * order.coupon.discount_percentage / 100) if order.coupon else 0
                for order in delivered_orders
            )

            # Calculate actual total price (before discounts)
            total_actual_price = sum(
                item.product.price * item.quantity
                for order in delivered_orders
                for item in order.orderitem_set.all()
            )

            # Calculate total offer discount
            total_offer_discount = sum(
                (item.product.price * item.quantity) - (item.price * item.quantity)
                for order in delivered_orders
                for item in order.orderitem_set.all()
            )

            # Create the report
            report = SalesReport.objects.create(
                user_admin=request.user,
                start_date=start_date,
                end_date=end_date,
                total_sales_delivered=total_sales_delivered,
                delivery_order_count=delivery_order_count,
                coupon_discount=coupon_discount,
                total_actual_price=total_actual_price,
                total_offer_discount=total_offer_discount
            )

            context = {
                'delivered_orders': delivered_orders,
                'total_sales_delivered': total_sales_delivered,
                'delivery_order_count': delivery_order_count,
                'coupon_discount': coupon_discount,
                'start_date': start_date,
                'end_date': end_date,
                'total_actual_price_of_product': total_actual_price,
                'total_offer_discount': total_offer_discount,
                'report': report
            }
            return render(request, 'my_admin/sales_report.html', context)

        return render(request, 'my_admin/sales_home.html')
    return redirect('admin_login')


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

# View to generate and download sales report PDF
def download_sales_report_pdf(request, pk):
    if request.user.is_staff:
        try:
            report = SalesReport.objects.get(pk=pk, user_admin=request.user)
        except SalesReport.DoesNotExist:
            return HttpResponse("Error: Sales report not found", status=400)

        delivered_orders = Order.objects.filter(
            created_at__range=[report.start_date, report.end_date], status='Delivered'
        ).filter(Q(is_return=False) | Q(return_status='Rejected'))

        context = {
            'delivered_orders': delivered_orders,
            'total_sales_delivered': report.total_sales_delivered,
            'delivery_order_count': report.delivery_order_count,
            'coupon_discount': report.coupon_discount,
            'start_date': report.start_date,
            'end_date': report.end_date,
            'total_actual_price_of_product': report.total_actual_price,
            'total_offer_discount': report.total_offer_discount
        }

        pdf = render_to_pdf('my_admin/sales_report_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
            return response
        return HttpResponse("Error generating PDF", status=500)
    return redirect('admin_login')

