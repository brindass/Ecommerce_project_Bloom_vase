from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import razorpay
from django.conf import settings
from user.models import Cart, CartItem, Address  
from .models import Order, OrderItem, OrderCancellation,ReturnReason
from .forms import OrderCancellationForm, ReturnReasonForm
from product.models import Product
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.paginator import Paginator


@login_required
def order_success(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    print("outide post")
    
    # if not cart or not cart.items.exists():
    #     messages.error(request, "Your cart is empty!")
    #     return redirect('view_cart')
    print(request.method)
    if request.method == 'POST':
        print(request.method)
        print("ita order success")
       
        address_id = request.POST.get('address')
        address = get_object_or_404(Address, id=address_id, user=user) 
        
        # order_items = []
        
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())
        payment_method = request.POST.get('payment_method')
        print('pY',payment_method)
        
        # if payment_method == 'razorpay':
        #     # Storing necessary data in session for Razorpay payment
        #     request.session['total_price'] = str(total_price)
        #     request.session['address_id'] = address_id
        #     request.session['order_items'] = [
        #         {
        #             'product_id': item.product.id,
        #             'quantity': item.quantity,
        #             'price': float(item.product.price)
        #         } for item in cart.items.all()
        #     ]
        #     return redirect('paymenthomepage')

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

        # order_items.append({
        #         'product_id': product.id,
        #         'quantity': item.quantity,
        #         'price': float(product_price) 
        #         })
        print(total_price)

        # messages.success(request, "Your order has been placed successfully!")
        return render(request, 'order/order_success.html', {'order': order})
    print("at alst")
    return redirect('view_cart')

def all_orders(request):
    user = request.user
    orders_list = Order.objects.filter(user=user).order_by('-created_at')
    
    # Pagination logic: Show 10 orders per page
    paginator = Paginator(orders_list, 10)  
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    return render(request, 'all-orders.html', {'orders': orders})
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    coupon = order.coupon
    print(coupon)
    if coupon:
        discount_price = (order.total_price * coupon.discount_percentage)/100
    else:
        coupon = None
        discount_price = None
    return render(request, 'order_details.html', {'order': order,'discount_price':discount_price})

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
    
# razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# def paymenthomepage(request):
#     total_price = Decimal(request.session.get('total_price', '0'))
#     currency = 'INR'
#     amount = int(total_price * 100)  # Convert to paise

#     # Create Razorpay order
#     razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
#     razorpay_order_id = razorpay_order['id']
#     callback_url = '/paymenthandler/'

#     context = {
#         'razorpay_order_id': razorpay_order_id,
#         'razorpay_merchant_key': settings.RAZOR_KEY_ID,
#         'razorpay_amount': amount,
#         'currency': currency,
#         'callback_url': callback_url,
#     }

#     return render(request, 'payment.html', context)


# @csrf_exempt
# def paymenthandler(request):
#     if 'user' not in request.session:
#         return redirect('user_login')

#     if request.method == 'POST':
#         try:
#             payment_id = request.POST.get('razorpay_payment_id', '')
#             razorpay_order_id = request.POST.get('razorpay_order_id', '')
#             signature = request.POST.get('razorpay_signature', '')

#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature,
#             }

#             result = razorpay_client.utility.verify_payment_signature(params_dict)
#             if result:
#                 total_price = Decimal(request.session.get('total_price', '0'))
#                 amount = int(total_price * 100)

#                 razorpay_client.payment.capture(payment_id, amount)

#                 user = request.user
#                 cart = Cart.objects.filter(user=user).first()
#                 address = get_object_or_404(Address, id=request.session['address_id'], user=user)
#                 order_items = request.session.get('order_items', [])

#                 # Create order
#                 order = Order.objects.create(
#                     user=user,
#                     total_price=total_price,
#                     street_address=address.street,
#                     city=address.city,
#                     district=address.district,
#                     state=address.state,
#                     pincode=address.pincode,
#                     payment='razorpay',
#                     payment_status='Paid',
#                 )

#                 for item in order_items:
#                     product = get_object_or_404(Product, id=item['product_id'])
#                     OrderItem.objects.create(
#                         order=order,
#                         product=product,
#                         quantity=item['quantity'],
#                         price=item['price'],
#                     )
#                     product.quantity -= item['quantity']
#                     product.save()

#                 cart.items.all().delete()

#                 # Clear session data
#                 del request.session['total_price']
#                 del request.session['order_items']
#                 del request.session['address_id']

#                 return render(request, 'order/order_success.html', {'order': order})

#             else:
#                 messages.error(request, "Payment verification failed. Please try again.")
#                 return redirect('view_cart')
#         except Exception as e:
#             print(e)
#             return render(request, 'paymentfail.html')

#     return HttpResponseBadRequest()

def order_pdf(request,order_id):
    user = request.user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    coupon = order.coupon
    # Calculate total order price
    total_order_price = sum(item.price * item.quantity for item in order_items)

    # Context for the template
    context = {
        'order': order,
        'order_items': order_items,
        'total_order_price': total_order_price,
        'user': user,
        'coupon': coupon,
    }

    # Load the HTML template
    template_path = 'order_pdf.html'
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response
