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
from .models import MyUser, Address, Cart, CartItem, Product
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.contrib.auth.hashers import make_password, check_password
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
    if 'user' in request.session:
        user = request.user
        addresses = user.addresses.all()  
        context = {'profile_user': user, 'addresses': addresses}
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
            return redirect('user_profile')
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
def add_to_cart(request,product_id):
    if request.method == 'POST':
        user = request.user
        product = get_object_or_404(Product,id = product_id)

        #Ensure product stock is sufficient
        if product.quantity <=0:
            messages.error(request, f"{product.name} is out of stock")
            return redirect('view_cart')
        
        cart, created = Cart.objects.get_or_create(user = user)
        cart_item, created = CartItem.objects.get_or_create(cart = cart, product = product)
        
        
        if not created:
            if cart_item.quantity > product.quantity:
                messages.error(request, f"only {product.quantity} items of {product.name} is available")
            else:
                cart_item.quantity += 1
                cart_item.save()

        # messages.success(request,f"{product.name} added to cart" )
        return redirect('view_cart')


# list products in cart
@login_required
def view_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user).first()  # Corrected filter condition
    if cart:
        cart_items = cart.items.all() if cart else []
    
    #calculate subtotal for each cart_item
    for item in cart_items:
        item.subtotal = item.product.price * item.quantity
    total = sum(item.product.price * item.quantity for item in cart_items)

    
    context = {'cart_items': cart_items,'total':total}
    return render(request, 'user/view_cart.html', context)



    
@login_required
def remove_from_cart(request, item_id):
    print('remove')
    cart_item = get_object_or_404(CartItem,id = item_id, cart__user = request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def update_cart_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = data.get('quantity')

        cart_item = get_object_or_404(CartItem,id = item_id, cart__user = request.user)
        cart_item.quantity = new_quantity
        cart_item.save() 

        #calculate subotal
        subtotal = cart_item.product.price * cart_item.quantity

        #calculate total for the cart
        cart = Cart.objects.get(user=request.user)
        cartitems = CartItem.objects.filter(cart=cart)
        total = sum(item.product.price * item.quantity for item in cartitems)
        print(total)

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



