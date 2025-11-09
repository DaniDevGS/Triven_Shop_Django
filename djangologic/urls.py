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
from django.urls import path
from products import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    #=================================VIEWS DE Trivens======================================================
    path('', views.index, name='index'),
    path('tienda/', views.products_store, name='tienda'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/add/', views.add_to_cart, name='add_to_cart'),
    path('carrito/remove/<int:producto_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('carrito/update/<int:producto_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('carrito/clear/', views.clear_cart, name='clear_cart'), # Opcional: si creas una vista para vaciar todo
    path('compra', views.compra_productos, name='compra_productos'),
    path('user_detail', views.user_details, name='user_detail'),
    path('tienda/<int:products_id>/', views.products_items, name='products_items'),

    #=================================VIEWS DE PRODUCTS Manager======================================================
    path('manager/', views.home, name='manage'),
    path('manager/products/', views.products, name='products'),
    path('manager/products_to_send/', views.products_to_send, name='products_to_send'),
    path('manager/product/create/', views.create_product, name='create_product'),
    path('manager/products/<int:products_id>/', views.product_detail, name='products_detail'),
    # urls.py
    path('manager/products/<int:products_id>/complete', views.sent_product, name='complete_products'), # type: ignore
    path('manager/products/<int:products_id>/delete', views.delete_product, name='delete_products'), # <-- Asegúrate de la coma # type: ignore
    #=================================VIEWS DE PRODUCTS Manager======================================================
    path('manager/pagos_verificados', views.pagos_verificar, name='pagos_verificados')
    
    # {% url 'pagos_verificados' %}

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)