from django.urls import path
from .views import (
    test, register, user_login, home, user_logout, verify_otp, resend_otp,
    user_profile, edit_profile, add_address, edit_address, delete_address,
    add_to_cart, view_cart, remove_from_cart, update_cart_item, forgot_password,
    verify_forgot_password_otp, reset_password, change_password, checkout, wishlist,
    add_to_wishlist, remove_from_wishlist, paymenthomepage, paymenthandler, add_funds
)
from user import views
urlpatterns =[
    path('',home,name='home'),
    path('register/',register,name = 'register'),
    path('verify-otp/<int:user_id>/', verify_otp, name='verify_otp'),  
    path('resend-otp/<int:user_id>/', resend_otp, name='resend_otp'),
    path('login/',user_login,name='user_login'),
    path('logout/',user_logout,name='user_logout'),
    path('user_profile/',user_profile,name='user_profile'),
    path('user_profile/edit/', edit_profile, name='edit_profile'),
    path('user_profile/address/add/', add_address, name='add_address'),
    path('user_profile/address/edit/<int:address_id>/', edit_address, name='edit_address'),
    path('user_profile/address/delete/<int:address_id>/', delete_address, name='delete_address'),
    path('cart/add/<int:product_id>/', add_to_cart, name ='add_to_cart'),
    path('cart/', view_cart, name ='view_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name ='remove_from_cart'),
    path('update_cart_item/', update_cart_item, name ='update_cart_item'),
    path('forgot_password/', forgot_password, name ='forgot_password'),
    path('verify_forgot_password_otp/<int:user_id>', verify_forgot_password_otp, name ='verify_forgot_password_otp'),
    path('reset_password/<int:user_id>', reset_password, name ='reset_password'),
    path('change_password/', change_password, name ='change_password'),
    path('checkout/', checkout, name='checkout'),
    path('wishlist/', wishlist, name= 'wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('paymenthomepage',paymenthomepage,name = 'paymenthomepage'),
    path('paymenthandler/', paymenthandler, name='paymenthandler'),
    path('add_funds/', add_funds, name= 'add_funds')

]
    