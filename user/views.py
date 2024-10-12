from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from .forms import CreateUserForm
from django.contrib.auth import authenticate, login, logout
import random
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .models import MyUser
from datetime import datetime

# Create your views here.

def test(request):
    form = CreateUserForm()
    context = {'form':form}
    return render(request,'user/test.html', context)

def register(request):
    print('Register view called')  # Debugging line
    form = CreateUserForm()
    if request.method == 'POST':
        print('Inside POST request')  # Debugging line
        form_data = request.POST.copy()
        print(form_data)
        form = CreateUserForm(form_data)
       
        
        if form.is_valid():

            
            print('Form is valid')  # Debugging line
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


# def register(request):
#     print('Register view called')  # Debugging line
#     if request.method == 'POST':
#         print('Inside POST request')  # Debugging line
#         print(request.POST)  # Debugging line to show POST data
        
#         form = CreateUserForm(request.POST)
        
#         if form.is_valid():
#             print('Form is valid')  # Debugging line
#             user = form.save(commit=False)

#             # Generate OTP
#             otp = random.randint(100000, 999999)
#             print('Generated OTP:', otp)
#             user.otp = otp
#             user.otp_expiry = timezone.now() + timedelta(minutes=5)  
#             user.save()

#             # Send OTP via email
#             subject = 'Your OTP for Registration'
#             message = f'Your OTP for registration is: {otp}. It will expire in 5 minutes.'
#             from_email = settings.EMAIL_HOST_USER
#             recipient_list = [user.email]

#             send_mail(subject, message, from_email, recipient_list)

#             return redirect('verify_otp', user_id=user.id)  # Redirect to OTP verification page
        
#         else:
#             print('Form is not valid:', form.errors)  # Debugging line to show form errors
#     else:
#         print('GET request')  # Debugging line for GET request
#         form = CreateUserForm()

#     context = {'form': form}  
#     return render(request, 'register.html', context)



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
    user.otp_expiry = timezone.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
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
        user = authenticate(request,email=email,password=password)
        if user is not None:
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


# @never_cache
# def loginpage(request):
#     if not request.user.is_authenticated:
#         if request.method == 'POST':
#             username = request.POST['username']
#             password = request.POST['password']
            
#             user = authenticate(request, username = username, password = password)
#             if user is not None:
#                 login(request,user)
#                 # request.session['username'] = username
#                 return redirect('home')
#             else:
#                 messages.error(request,"Invalid username or password")
#                 return redirect('login')
#         return render(request,'login.html')
    
#     return redirect('home')

# def signup_page(request):
#      if request.method == 'POST':
#         username = request.POST['username']
#         first_name = request.POST['firstname']
#         password = request.POST['password']
#         password1= request.POST['password1']
#         email    = request.POST['email']

#         if password == password1:
#             if User.objects.filter(username=username).exists():
#                 messages.error(request, 'Username already exists')
#                 return redirect('signup')
#             else:
#                 user = User.objects.create_user(username, email, password)
#                 user.first_name = first_name
#                 user.save()
#                 messages.success(request, 'You have successfully signed up!')
#                 return redirect('login')
#         else:
#             messages.error(request, 'Passwords do not match')
#             return redirect('signup')
    
#      else:
#          return render(request,'signup.html')