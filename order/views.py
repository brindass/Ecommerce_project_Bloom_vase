from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import Cart, CartItem, Address  
from .models import Order, OrderItem, OrderCancellation,ReturnReason
from .forms import OrderCancellationForm, ReturnReasonForm

@login_required
def order_success(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    print("outide post")
    
    # if not cart or not cart.items.exists():
    #     messages.error(request, "Your cart is empty!")
    #     return redirect('view_cart')
    
    if request.method == 'POST':
        print("ita order success")
       
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id, user=user) 
        
        
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())
        payment_method = request.POST.get('payment')  
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            street_address=address.street,
            city=address.city,
            district=address.district,
            state=address.state,
            pincode=address.pincode,
            payment=payment_method,
            payment_status='Pending',
        )

       
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            
            item.product.quantity -= item.quantity
            item.product.save()
        
        cart.items.all().delete()

        # messages.success(request, "Your order has been placed successfully!")
        return render(request, 'order/order_success.html', {'order': order})
    print("at alst")
    return redirect('view_cart')


def all_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request,'all-orders.html',{'orders':orders})

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_details.html', {'order': order})

@login_required
def cancel_order(request, order_id):
   
    order = get_object_or_404(Order, id=order_id, user=request.user)
    print(order)
    # if order.status in ['Delivered', 'Cancelled']:

    #     messages.error(request, "This order cannot be cancelled.")
    #     return redirect('all_orders')

    if request.method == 'POST':
        print(request)
        form = OrderCancellationForm(request.POST)
        if form.is_valid():
            print('inside')
            order.status = 'cancellation requested'
            # order.is_cancelled = True
            order.save()

            # Create a cancellation record
            OrderCancellation.objects.create(
                order=order,
                reason=form.cleaned_data['reason'],
                cancel_status='pending'
            )
            messages.success(request, "Your cancellation request has been submitted.")
            return redirect('order_success')
    else:
        form = OrderCancellationForm()
        return render(request, 'order_cancel.html', {'form': form, 'order': order})

@login_required
def return_request(request, order_id):
   
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Validate the order's eligibility for return
    if order.status not in ['Delivered']:
        messages.error(request, "You can only request returns for delivered orders.")
        return redirect('all_orders')  

    if request.method == 'POST':
        form = ReturnReasonForm(request.POST)
        if form.is_valid():
           
            order.is_return = True
            order.return_status = 'Return Requested'
            order.save()

            # Save the return reason
            ReturnReason.objects.create(
                order=order,
                reason=form.cleaned_data['reason']
            )

            messages.success(request, "Your return request has been submitted.")
            return redirect('order_success')  # Redirect after successful submission
    else:
        form = ReturnReasonForm()

    return render(request, 'return_request.html', {'form': form, 'order': order})
    
