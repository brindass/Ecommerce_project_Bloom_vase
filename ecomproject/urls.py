"""
URL configuration for ecomproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from . import settings
# from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('user/',include('user.urls')),
    path('',include('product.urls')),
    # path('',views.loginpage,name='login'),
    path('my_admin/',include('my_admin.urls')),
    path('order/', include('order.urls')),
    path('accounts/', include('allauth.urls')),
    # path('home/',views.Homepage,name='home'),
    # path('logout/',views.Logoutpage,name='logout'),
    # path('signup/',views.signup_page,name='signup'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) 

