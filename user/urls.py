from django.urls import path
from .views import test, register, user_login, home, user_logout, verify_otp, resend_otp
from user import views
urlpatterns =[
    # path('',home,name='home'),
    path('register/',views.register,name = 'register'),
    path('verify-otp/<int:user_id>/', verify_otp, name='verify_otp'),  
    path('resend-otp/<int:user_id>/', resend_otp, name='resend_otp'),
    path('login/',user_login,name='user_login'),
    path('logout/',user_logout,name='user_logout')
]
    