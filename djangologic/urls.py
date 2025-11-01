"""
URL configuration for djangologic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from products import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    #=================================VIEWS DE PRODUCTS Manager======================================================
    path('manager/', views.home, name='home'),
    path('manager/signup/', views.signup, name='signup'),
    path('manager/logout/', views.signout, name='logout'),
    path('manager/signin/', views.signin, name='signin'),
    path('manager/products/', views.products, name='products'),
    path('manager/products_to_send/', views.products_to_send, name='products_to_send'),
    path('manager/product/create/', views.create_product, name='create_product'),
    path('manager/products/<int:products_id>/', views.product_detail, name='products_detail'),
    # urls.py
    path('manager/products/<int:products_id>/complete', views.sent_product, name='complete_products'), # type: ignore
    path('manager/products/<int:products_id>/delete', views.delete_product, name='delete_products'), # <-- Asegúrate de la coma # type: ignore


    #=================================VIEWS DE Trivens======================================================
    path('', views.index, name='index'),
    path('tienda/', views.products_store, name='tienda')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)