from django.urls import path
from .views import (
    test, list_users, block_or_unblock_user, delete_category, 
    add_category, update_category, create_product, update_product, 
    delete_product, admin_login, list_order, order_details, 
    admin_cancel_update, cancel_reject, cancel_approve, add_category_offer,
    list_category_offers, edit_category_offer,  delete_category_offer,  add_product_offer,
    list_product_offers, edit_product_offer, delete_product_offer, list_coupon, add_coupon,
    edit_coupon, apply_coupon,  delete_coupon


)

urlpatterns = [
    path('admin_login/',admin_login,name ='admin_login'),
    path('users/',list_users,name ='list_users'),
    path('block_unblock/<int:pk>/',block_or_unblock_user,name ='block_unblock'),
    path('category/',add_category,name ='add_category'),
    path('delete_category/<int:pk>/',delete_category,name ='delete_category'),
    path('update_category/<int:pk>/',update_category,name ='update_category'),
    path('update_product/',update_product,name ='update_product'),
    path('products/',create_product,name ='create&list_product'),
    path('delete_product/<int:pk>/',delete_product,name ='delete_product'),
    path('orders/', list_order, name = 'list_order'),
    path('orders/<int:order_id>', order_details, name = 'admin_order_details'),
    path('admin_cancel_update/', admin_cancel_update, name ='admin_cancel_update'),
    path('cancel_approve/<int:pk>/',cancel_approve, name='cancel_approve'),
    path('cancel_reject/<int:pk>/', cancel_reject, name='cancel_reject'),

    path('add-category-offer/', add_category_offer, name='add_category_offer'),
    path('list-category-offers/', list_category_offers, name='list_category_offers'),
    path('edit-category-offer/<int:pk>/', edit_category_offer, name='edit_category_offer'),
    path('delete-category-offer/<int:pk>/', delete_category_offer, name='delete_category_offer'),

    path('add-product-offer/', add_product_offer, name='add_product_offer'),
    path('list-product-offers/', list_product_offers, name='list_product_offers'),
    path('edit-product-offer/<int:pk>/', edit_product_offer, name='edit_product_offer'),
    path('delete-product-offer/<int:pk>/', delete_product_offer, name='delete_product_offer'),

    path('list-coupon/', list_coupon, name='list_coupon'),
    path('add-coupon/', add_coupon, name='add_coupon'),
    path('list-coupon/', list_coupon, name='list_coupon'),
    path('edit-coupon/<int:pk>/', edit_coupon, name='edit_coupon'),
    path('apply-coupon/', apply_coupon, name='apply_coupon'),
    path('delete-coupon/<int:pk>/', delete_coupon, name='delete_coupon'),
    

]


