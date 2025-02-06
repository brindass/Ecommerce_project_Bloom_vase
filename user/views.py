from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from .forms import CreateUserForm, EditProfileForm, AddressForm
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import MyUser, Address, Cart, CartItem, Product, ProductVariant, Wishlist, WishlistItem, Wallet, Transaction
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import make_password, check_password
from order.models import Order, OrderItem
from decimal import Decimal
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.urls import reverse
from product.views import get_discounted_price
from django.core.paginator import Paginator
from my_admin.models import Coupon
from django.http import HttpResponse

# Create your views here.

def test(request):
    form = CreateUserForm()
    context = {'form':form}
    return render(request,'user/test.html', context)

def register(request):
    print('Register view called') 
    form = CreateUserForm()
    if request.method == 'POST':
        print('Inside POST request')  
        form_data = request.POST.copy()
        print(form_data)
        form = CreateUserForm(form_data)
       
        
        if form.is_valid():

            
            print('Form is valid')  
            user = form.save(commit=False)

            # Generate OTP
            otp = random.randint(100000, 999999)
            print(otp)
            request.session['otp'] = otp
            # user.otp = otp
            otp_expiry = timezone.now() + timedelta(minutes=5)
            request.session['otp_expiry'] = otp_expiry.isoformat()   
            user.save()

            # OTP to user mail
            subject = 'Your OTP for Registration'
            message = f'Your OTP for registration is: {otp}. It will expire in 5 minutes.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)

            return redirect('verify_otp', user_id=user.id) # redirect to OTP verification page

            # return redirect('login')

        else:
            print(form.errors)
    context = {'form':form}  
    return render(request,'user/register.html',context) 





def verify_otp(request, user_id):
    print('inside verify_otp')
    user = get_object_or_404(MyUser, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_expiry = datetime.fromisoformat(request.session.get('otp_expiry'))

        
        if int(entered_otp) == request.session.get('otp') and timezone.now() < otp_expiry:
            user.is_active = True  
            user.save()
            return redirect('user_login')
        else:
            print("Invalid or expired OTP")
            return redirect('verify_otp', user_id=user.id)

    return render(request, 'user/otp_verification.html')


def resend_otp(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    
    # Generate new OTP
    otp = random.randint(100000, 999999)
    user.otp = otp
    user.otp_expiry = timezone.now() + timedelta(minutes=5) 
    user.save()

    # Send the new OTP via email
    subject = 'Your New OTP'
    message = f'Your new OTP is: {otp}. It will expire in 5 minutes.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    send_mail(subject, message, from_email, recipient_list)

    return redirect('verify_otp', user_id=user.id)




# otp = ''
# for i in range(6):
#     otp += str(random.randint(0,9))

# print(otp)

# server = smtplib.SMTP('smtp.gmail.com',587)
# server.starttls()

# server.login('brindass49@gmail.com','jiwe btfl aoin aeip')

def user_login(request):
    print('inside login')
    if request.method =='POST':
        email = request.POST.get('email')
        print(email)
        password = request.POST.get('password')
        print(password)
        
        user = authenticate(request,email=email,password=password)


        if user is not None:
            request.session['user'] = user.email
            print(request.session['user'])
            login(request,user)
            return redirect('home')
            
        else:
            print("user not found")
            return redirect('user_login')
    return render(request,'user/login.html')

def user_logout(request):
    logout(request)
    return redirect('user_login')



@never_cache
def home(request):
    if request.user.is_authenticated:
        return render(request,'product/home.html')
    return redirect('user_login')

# user profile details
@login_required
def user_profile(request):
    if request.user.is_authenticated:
        user = request.user
        addresses = user.addresses.all()  

        wallet = get_object_or_404(Wallet, user=user)

        transactions = Transaction.objects.filter(wallet=wallet).order_by('-transaction_date')

        # Paginate transactions (5 per page)
        paginator = Paginator(transactions, 5)
        page_number = request.GET.get('page', 1)
        transactions = paginator.get_page(page_number)
        
        context = {'profile_user': user, 'addresses': addresses, 'wallet': wallet, 'transactions': transactions}
            
        return render(request, 'user/user_profile.html', context)
    return redirect('user_login')

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
        else:
            context = {'form': form}
            messages.error(request, "Invalid User details")
    else:
        form = EditProfileForm(instance=user)
        context = {'form': form}
    return render(request, 'user/edit_profile.html', context)


# Manage addresses 

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            print(user)
            address = form.save(commit=False)
            address.users = user 
            address.save()
            
        
            next_url = request.GET.get('next', 'user_profile')
            return redirect(next_url)
    else:
        form = AddressForm() 
    context = {'form': form}
    return render(request, 'user/add_address.html', context)

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, users=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = AddressForm(instance=address)
        context = {'form': form }
    return render(request, 'user/edit_address.html', context)

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, users=request.user)
    address.delete()
    return redirect('user_profile')

# cart 
@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        user = request.user
        page = request.POST.get('page')
        variant = None

        if page == "variants_page":
            variant = get_object_or_404(ProductVariant, id=product_id)
        elif page == "product_page":
            product = get_object_or_404(Product, id=product_id)
            variant = product.variants.filter(is_default=True).first()  # Get default variant

        if not variant:
            messages.error(request, "No variant available for this product.")
            return redirect('product_details', pk=product_id)

        if variant.quantity <= 0:
            messages.error(request, f"{variant.product.name} - {variant.color} is out of stock")
            return redirect('product_details', pk=product_id)

        # Create or retrieve cart
        cart, created = Cart.objects.get_or_create(user=user)

        # Add item to cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=variant.product, variant=variant)

        # Update quantity
        if not created:
            if cart_item.quantity >= variant.quantity:
                messages.error(request, f"Only {variant.quantity} items available")
            else:
                cart_item.quantity += 1
                cart_item.save()
        else:
            cart_item.quantity = 1
            cart_item.save()

        messages.success(request, f"{variant.product.name} - {variant.color} added to cart")
        return redirect('view_cart')

# list products in cart
@login_required
def view_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    cart_items = cart.items.all() if cart else []

    for item in cart_items:
        if item.variant:
            discounted_price = get_discounted_price(item.variant.product)
            item.discounted_price = discounted_price
            item.subtotal = discounted_price * item.quantity
            item.variant_name = f"{item.variant.product.name} - {item.variant.color}"
        else:
            discounted_price = get_discounted_price(item.product)
            item.discounted_price = discounted_price
            item.subtotal = discounted_price * item.quantity
            item.variant_name = None

    total = sum(item.subtotal for item in cart_items)

    context = {'cart_items': cart_items, 'total': total}
    return render(request, 'user/view_cart.html', context)



    
@login_required
def remove_from_cart(request, item_id):
    print('remove')
    cart_item = get_object_or_404(CartItem,id = item_id, cart__user = request.user)
    print(cart_item)
    cart_item.delete()
    return redirect('view_cart')



@login_required
def update_cart_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = data.get('quantity')

        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        if new_quantity > cart_item.variant.quantity:
            return JsonResponse({'error': f"Only {cart_item.variant.quantity} items available"}, status=400)

        cart_item.quantity = new_quantity
        cart_item.save()

        discounted_price = get_discounted_price(cart_item.product)
        item_price = discounted_price if discounted_price < cart_item.product.price else cart_item.product.price
        subtotal = item_price * cart_item.quantity

        cart = Cart.objects.get(user=request.user)
        total = sum(
            (get_discounted_price(item.variant.product) * item.quantity if item.variant else get_discounted_price(item.product) * item.quantity)
            for item in cart.items.all()
        )

        return JsonResponse({'subtotal': subtotal, 'total': total})

    return JsonResponse({'error': 'Invalid request'}, status=400)



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = MyUser.objects.get(email=email)
            otp = random.randint(100000,999999)
            print(otp)
            request.session['forgot_otp'] = otp
            otp_expiry = timezone.now() + timedelta(minutes=5)
            request.session['forgot_otp_expiry'] = otp_expiry.isoformat()
            request.session['user_id'] = user.id

            subject = 'Your OTP for Password Reset'
            message = f'Your OTP for Password Reset is: {otp}. It will expire in 5 minutes.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            send_mail(subject, message, from_email, recipient_list) 
            return redirect('verify_forgot_password_otp', user_id=user.id)
        except MyUser.DoesNotExist:
            messages.error(request,"No User found with this email")
            return redirect('forgot_password')
    return render(request,'user/forgot_password.html')

def verify_forgot_password_otp(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_expiry = datetime.fromisoformat(request.session.get('forgot_otp_expiry'))
    
        if int(entered_otp) == request.session.get('forgot_otp') and timezone.now() < otp_expiry:
            return redirect('reset_password', user_id=user.id)
        else:
            messages.error(request,"Invalid or expired OTP")
            return redirect('verify_forgot_password_otp', user_id=user.id)
        
    context = {'user': user}
    
    return render(request,'user/verify_forgot_password_otp.html',context)

def reset_password(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    print(user_id)

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password= request.POST.get('confirm_password')
        print(new_password)
        
        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.save()
            messages.success(request,"Your Password has been reset successfully.")
            return redirect('user_login')
        else:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password', user_id=user.id)
    context = {'user': user}
    return render(request, 'user/reset_password.html',context)

@login_required
def change_password(request):
    user = request.user
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        print(confirm_password)

        if not check_password(current_password, user.password):
            messages.error(request,"Current password is incorrect.")
            return redirect('change_password')

        if new_password != confirm_password:
            messages.error(request,"New passwords do not match")
            return redirect('change_password')

        user.password = make_password(new_password)
        user.save()
        
        update_session_auth_hash(request,user)
        messages.success(request,"Password changed successfully.")
        return redirect('user_profile')
    
    return render(request, 'user/change_password.html')

# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))


def checkout(request):
    user = request.user

    # Ensure the user has a wallet
    wallet, created = Wallet.objects.get_or_create(user=user)

    # Check if user has a cart
    cart = Cart.objects.filter(user=user).first()
    if not cart or cart.items.count() == 0:
        messages.error(request, "Your cart is empty. Add items before proceeding to checkout.")
        return redirect('view_cart')

    # Fetch addresses and calculate cart total
    addresses = user.addresses.all()

    cart_items = cart.items.select_related('product', 'variant')  # Ensure variant is fetched

    
    # Calculate total price with discounts
    total_price = Decimal('0.00')
    for item in cart_items:
        # Use get_discounted_price to calculate the best price
        product_price = get_discounted_price(item.product)
        variant_price = get_discounted_price(item.variant.product) if item.variant else None
        print("name of hre prfj",item.product.name, item.product.category)
        discounted_price = variant_price if variant_price else product_price
        print("Hii",discounted_price)
        item.discounted_price = discounted_price
        item.total_price = discounted_price * item.quantity
        total_price += item.total_price
        item.save()

    # Handle coupon
    # Use session-stored coupon discount if available

    coupon_code = request.session.get('coupon', None)
    print(coupon_code) 
    coupon_discount = Decimal(request.session.get('coupon_discount', '0.00'))

    # coupon = Coupon.objects.get(coupon_code=coupon, is_active=True)
    # print('coup',coupon)

    # If user removes the coupon
    if request.POST.get('remove_coupon'):
        request.session.pop('coupon', None)
        request.session.pop('coupon_discount', None)
        messages.success(request, "Coupon removed successfully.")
        return redirect('checkout')

    total_price -= coupon_discount  # Apply discount if present
    print('coupon',total_price)
    # return render(request, 'checkout.html', {
    #     'total_price': total_price,
    #     'coupon_code': coupon_code,
    #     'coupon_discount': coupon_discount
    # })

    
    if request.method == 'POST':
        print('hi')
        # Handle form submission
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        coupon_code = request.POST.get('coupon', None)
        print('coopon_code:',coupon_code)
        
        if not address_id or not payment_method:
            messages.error(request, "Please select a valid address and payment method.")
            return redirect('checkout')

        # Validate address
        address = get_object_or_404(Address, id=address_id, users=user)

        # coupon = Coupon.objects.get(coupon_code=coupon_code, is_active=True)
        # print('coup',coupon)

        coupon = None

        if coupon_code:
            try:
                total_price = Decimal(total_price)  
                coupon = Coupon.objects.get(coupon_code=coupon_code, is_active=True)

                if total_price >= coupon.min_purchase_amount:
                    discount_amount = (coupon.discount_percentage / Decimal(100)) * total_price
                    total_price = total_price - discount_amount
                    request.session['coupon'] = coupon.coupon_code
                    print('Total price after coupon_applied:',total_price)
                else:
                    return HttpResponse("Error: Minimum purchase amount for the coupon is not met")
            except Coupon.DoesNotExist:
                return HttpResponse("Error: Invalid coupon code")

        # Handle wallet payment
        if payment_method == 'wallet':
            wallet = get_object_or_404(Wallet,user=user)
            transaction = Transaction.objects.filter(wallet=wallet)
            if wallet.amount >= total_price:
                wallet.debit(total_price)
                wallet.save()

                # Create order
                order = Order.objects.create(
                    user=user,
                    total_price=total_price,
                    street_address=address.street,
                    city=address.city,
                    district=address.district,
                    state=address.state,
                    pincode=address.pincode,
                    payment=payment_method,
                    payment_status='Completed',
                    coupon=coupon if coupon else None
                )
                # Create order items and update variant/product quantities
                for item in cart_items:
                    print(item)
            # Check variant stock if a variant exists
                # Update stock
                if item.variant:
                    if item.variant.quantity >= item.quantity:
                        item.variant.quantity -= item.quantity
                        item.variant.save()
                    else:
                        messages.error(request, f"Insufficient stock for {item.variant.product.name}.")
                        return redirect('view_cart')
                else:
                    if item.product.quantity >= item.quantity:
                        item.product.quantity -= item.quantity
                        item.product.save()
                    else:
                        messages.error(request, f"Insufficient stock for {item.product.name}.")
                        return redirect('view_cart')


                # Create order item
                OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=item.total_price / item.quantity,  # Per-item price
            )

            else:
                messages.error(request,'Insufficient wallet balance')
                return redirect('checkout')
        # Clear the cart
            cart.items.all().delete()

            Transaction.objects.create(wallet = wallet,amount = order.total_price,transaction_type = 'debit')

            messages.success(request, "Your order has been placed successfully!")
            return render(request, 'order_success.html', {'orders': order})
        # else:
        #     messages.error(request,'insufficient wallet balance')
            # return redirect('checkout')

        # Handle Razorpay payment method
        if payment_method == 'razorpay':
            request.session['total_price'] = str(total_price)
            request.session['address_id'] = address.id
            request.session['order_items'] = [
                {
                    'product_id': item.product.id,
                    'variant_id': item.variant.id if item.variant else None,
                    'quantity': item.quantity,
                    'price': float(item.discounted_price),
                } for item in cart_items
            ]
            return redirect('paymenthomepage')
            

        # Create order
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
            coupon=coupon if coupon else None
        )

        # Create order items and update variant/product quantities
        for item in cart_items:
            print(item)
            # Check variant stock if a variant exists
            if item.variant:
                if item.variant.quantity >= item.quantity:
                    item.variant.quantity -= item.quantity
                    print(item.variant.quantity)
                    item.variant.save()
                else:
                    messages.error(request, f"Insufficient stock for {item.variant.product.name}.")
                    return redirect('view_cart')
                price = item.discounted_price
                print(price)
            else:
                # Check product stock
                if item.product.quantity >= item.quantity:
                    item.product.quantity -= item.quantity
                    item.product.save()
                else:
                    messages.error(request, f"Insufficient stock for {item.product.name}.")
                    return redirect('view_cart')
                price = item.discounted_price
                print(price)

            # Create order item
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=price,
            )

        # Clear the cart
        cart.items.all().delete()

        messages.success(request, "Your order has been placed successfully!")
        return render(request, 'order_success.html', {'orders': order})
    

    # Render checkout page
    context = {
        'addresses': addresses,
        'cart_items': cart_items,
        'total': total_price,
        'coupon_discount': coupon_discount,
        'coupon_code': coupon_code,
    }
    return render(request, 'user/checkout.html', context)


@login_required
def wishlist(request):
    user = request.user
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    wishlist_items = wishlist.wishlist_items.all()
    return render(request, 'user/wishlist.html', {'wishlist': wishlist, 'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        variant_id = request.POST.get('variant_id')
        print(variant_id)
        variant = ProductVariant.objects.filter(id=variant_id).first() if variant_id else None

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        if not WishlistItem.objects.filter(wishlist=wishlist, product=product, variant=variant).exists():
            WishlistItem.objects.create(wishlist=wishlist, product=product, variant=variant)
            return JsonResponse({'status': 'success', 'message': f"{product.name} added to your wishlist."})
        else:
            return JsonResponse({'status': 'info', 'message': f"{product.name} is already in your wishlist."})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


@login_required
def remove_from_wishlist(request, product_id):
    print(request.method)
    if request.method == 'POST' or request.method == 'GET' :
        wishlist = Wishlist.objects.get(user=request.user)
        item = get_object_or_404(WishlistItem, wishlist=wishlist, product__id=product_id)
        item.delete()
        return JsonResponse({'status': 'success', 'message': "Item removed from your wishlist."})

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})


def paymenthomepage(request):
    total_price = Decimal(request.session.get('total_price', '0'))
    print(total_price)
    currency = 'INR'
    amount = int(total_price * 100)  # Convert to paise

    # Create Razorpay order
    razorpay_order = razorpay_client.order.create(dict(amount=amount, currency=currency, payment_capture='0'))
    razorpay_order_id = razorpay_order['id']
    callback_url ='paymenthandler/'
    print(razorpay_order_id)
    print(callback_url)
    # name = "Bloom and vase"

    context = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url,
       
    }

    return render(request, 'payment.html', context)



@csrf_exempt
def paymenthandler(request):
    print("payment")
    

    if request.method == 'POST':
        print('request',request)
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result:
                total_price = Decimal(request.session.get('total_price', '0'))
                amount = int(total_price * 100)

                razorpay_client.payment.capture(payment_id, amount)

                user = request.user
                if user:
                    print(user)
                else:
                    print('user none')
                cart = Cart.objects.filter(user=user).first()
                address = get_object_or_404(Address, id=request.session['address_id'], users=user)
                print(address)
                order_items = request.session.get('order_items', [])
                coupon_code = request.session.get('coupon',None)
                print(coupon_code)
                print('razorpay order created')
                coupon = None

                if coupon_code:
                    try:
                        coupon = Coupon.objects.get(coupon_code=coupon_code, is_active = True)
                    except Coupon.DoesNotExist:
                        coupon = None
                        
                        

                # Create order
                order = Order.objects.create(
                    user =user,
                    total_price=total_price,
                    street_address=address.street,
                    city=address.city,
                    district=address.district,
                    state=address.state,
                    pincode=address.pincode,
                    payment='razorpay',
                    payment_status='Paid',
                    coupon=coupon
                )

                for item in order_items:
                    for i in item:
                        print(i)
                    variant = get_object_or_404(ProductVariant, id=item['variant_id'])
                    OrderItem.objects.create(
                        order=order,
                        product=variant.product,
                        quantity=item['quantity'],
                        price=item['price'],
                    )
                    variant.quantity -= item['quantity']
                    variant.save()

                cart.items.all().delete()

                # Clear session data
                del request.session['total_price']
                del request.session['order_items']
                del request.session['address_id']

                return render(request,'order_success.html')

            else:
                messages.error(request, "Payment verification failed. Please try again.")
                return redirect('view_cart')
        except Exception as e:
            print(e)
            return render(request, 'paymentfail.html')

    return HttpResponseBadRequest()

@login_required
def add_funds(request):
    user = request.user
    wallet, created = Wallet.objects.get_or_create(user=user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            amount = Decimal(amount)
            wallet.credit(amount)
            Transaction.objects.create(wallet=wallet, transaction_type='credit', amount=amount)
            messages.success(request, f"Successfully added ${amount} to your wallet.")
            return redirect('user_profile')

    return render(request, 'user/add_funds.html', {'wallet': wallet})

