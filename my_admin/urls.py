from django.urls import path
from .views import (
    test, list_users, block_or_unblock_user, delete_category, 
    add_category, update_category, create_product, update_product, 
    delete_product, admin_login, list_order, order_details, 
    admin_cancel_update, cancel_reject, cancel_approve
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

]
