from django.shortcuts import render
from user.models import MyUser 
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from product.models import Category, Product
from product.forms import ProductForm, ProductVariantFormSet
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from order.models import Order,OrderItem, OrderCancellation

# Create your views here.
def test(request):
    return render(request,'my_admin/category.html')

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
    if 'admin' in request.session:
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
    if 'admin' in request.session:
        user = get_object_or_404(MyUser, id=pk)
        user.is_active = not user.is_active
        messages.success(request, f'User {user.email} status changed.')
        user.save()
        return redirect('list_users') 

def add_category(request):
    if 'admin' in request.session:
        if request.method == 'POST':
            name = request.POST.get('name').strip()
            if name:
                Category.objects.create(name=name)
        categories = Category.objects.all()
        context = {'categories':categories}
        print(context)
        return render(request,'my_admin/category.html',context)


def update_category(request,pk):
    if 'admin' in request.session:
        if request.method == 'POST':
            category = Category.objects.get(id=pk)
            name = request.POST.get('name')
            category.name = name
            category.save()
            return redirect('add_category')
     

def delete_category(request,pk):
    if 'admin' in request.session:
        category = Category.objects.get(id=pk)
        category.inactive = not category.inactive
        category.save()
        return redirect('add_category')


def create_product(request):
    if 'admin' in request.session:
        form = ProductForm()
        formset = ProductVariantFormSet()

        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save()  # Save the product
                formset = ProductVariantFormSet(request.POST, request.FILES, instance=product)
                if formset.is_valid():
                    formset.save()  # Save variants
                    return redirect('create&list_product')
                else:
                    print("Variant Formset Errors:", formset.errors)

        products = Product.objects.all()
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
    if 'admin' in request.session:
        form = ProductForm()
        if request.method == 'POST':
            # Print the data being sent to the view
            print("POST Data: ", request.POST)
            print("FILES Data: ", request.FILES)

            # Fetch the product if it's an update, otherwise create a new one
            product_id = request.POST.get('id')
            if product_id:
                product = Product.objects.get(id=product_id)  # Update existing product
                form = ProductForm(request.POST, request.FILES, instance=product)

                if form.is_valid():
                    product = form.save()
                else:
                    print(form.errors)

                # Redirect to a success page or reload the page
                return redirect('create&list_product')
            else:
                # Print form errors if there are any
                print("Form Errors: ", form.errors)
        # else:
        #     form = ProductForm()
        
        # return render(request, 'product_list.html', {'form': form})
        return redirect('create&list_product')
    

def delete_product(request,pk):
    if 'admin' in request.session:
        product = Product.objects.get(id=pk)
        product.soft_deleted = not product.soft_deleted
        product.save()
        return redirect('create&list_product')

def list_order(request):
    if 'admin' in request.session:
        search = request.GET.get('q', '')
        print("Search Query: ", search)

        if request.method == "POST":
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('new_status')
            print(f"Order ID: {order_id}, New Status: {new_status}")
            
            try:
                order = Order.objects.get(pk=order_id)
                print("Order User: ", order.user)

                if order.is_return:
                    order.return_status = new_status
                    if new_status == 'Returned':
                        order.save()
                    elif new_status == 'Delivered':
                        order.payment_status = 'Paid'
                        order.save()

                if new_status == "Cancelled":
                    print("Order Cancelled")
                    order_items = OrderItem.objects.filter(order=order)
                    for item in order_items: 
                        item.product.quantity += item.quantity
                        item.product.save()

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
    if 'admin' in request.session:
        order = get_object_or_404(Order, id=order_id)
        order_items = OrderItem.objects.filter(order=order)

        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'my_admin/admin_order_details.html', context)
    
def admin_cancel_update(request):
    if 'admin' in request.session:
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
    if 'admin' in request.session:
        cancellation = get_object_or_404(OrderCancellation, id=pk)
        order = cancellation.order

        # Update stock for order items
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            item.product.quantity += item.quantity
            item.product.save()

        # Update order and cancellation status
        order.is_cancelled = True
        order.status = 'cancelled'
        order.save()

        cancellation.cancel_status = 'approved'
        cancellation.save()
        messages.success(request, f"Cancellation request for Order #{order.id} has been approved.")
        return redirect('admin_cancel_update')
    return redirect('admin_login')


def cancel_reject(request, pk):
    if 'admin' in request.session:
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