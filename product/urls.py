from django.urls import path
from .views import list_product, test, product_details

urlpatterns = [
    path('',list_product,name='home'),
    path('test',test,name='test'),
    # path('create/',create_product,name='create_product'),
    # path('update/<int:pk>/',update_product,name='update_product'),
    # path('delete/<int:pk>/',delete_product,name='delete_product'),
    # path('retrieve/<int:pk>/',retrieve_product,name='retrieve_product'),
    path('product/<int:pk>/',product_details,name='product_details')
    
]
    
