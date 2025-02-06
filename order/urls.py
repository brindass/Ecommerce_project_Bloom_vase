from django.urls import path
from .views import order_success,all_orders, order_details, cancel_order, return_request, order_pdf
from order import views


urlpatterns = [
    path('success/', order_success, name='order_success'),
    path('all-orders/',all_orders , name='order_success'),
    path('order/<int:order_id>/', order_details, name='order_details'),
    path('cancel/<int:order_id>/', cancel_order,name='cancel_order'),
    path('order/<int:order_id>/return', return_request, name='return_request'),
    path('order/<int:order_id>/pdf/', order_pdf, name='order_pdf'),
   

]