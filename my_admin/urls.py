from django.urls import path
from .views import test ,list_users, block_or_unblock_user, delete_category, add_category, update_category, create_product, update_product, delete_product, admin_login

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
]
