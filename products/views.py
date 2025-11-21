from django.shortcuts import render, redirect, get_object_or_404
# Asegúrate de importar Q si no lo has hecho, es vital para combinaciones de filtros OR/AND
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import ProductForm
from .serializers import ItemSerializer
from .models import Producto, CATEGORIA_CHOICES, ProductoImagen, Carrito, ItemCarrito, OrdenDeCompra, ItemOrden # <--- IMPORTANTE: Importar Carrito e ItemCarrito
from django.contrib import messages
from.conversion import get_exchange_rate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.views.decorators.http import require_POST # <--- Importar require_POST
import uuid # Para generar el ID único
from io import BytesIO # Para manejar el PDF en memoria
from django.core.files.base import ContentFile # Para guardar archivos
from django.db import transaction # Para asegurar la integridad de la reducción de stock
import urllib.parse # Para codificar el mensaje de WhatsApp

# Create your views here.
# Create your views here.

# ===============================================================================================================
#===================================DJANGO ==================================================================
# ===============================================================================================================

def home(request):
    """Renderiza la página de inicio.

    Esta vista simplemente devuelve la plantilla 'home.html'.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que renderiza 'home.html'.
    """
    return render(request, 'manager/home.html')


# =====================================================SECCION PRODUCTS===================================================================
@login_required
def products(request):
    productos = Producto.objects.filter(datecompleted__isnull=True)
    return render(request, 'manager/products.html', {'productos': productos , 'sent_view': False})

@login_required
def products_to_send(request):
    productos = Producto.objects.filter(datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'manager/products.html', {'productos': productos, 'sent_view': True})

@login_required
def create_product(request):
    if request.method == 'GET':
        return render(request, 'manager/create_product.html', {
            'form': ProductForm
        })
    else:
        try:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                new_product = form.save(commit=False)
                new_product.user = request.user
                new_product.save()
                
                # === LÓGICA CORREGIDA PARA MULTIPLE FILE FIELD ===
                # Gracias al MultipleFileField en forms.py, 'imagenes_extra' ya es una lista limpia
                images = form.cleaned_data.get('imagenes_extra')
                
                if images: 
                    for img in images:
                        ProductoImagen.objects.create(producto=new_product, imagen=img)
                # =================================================
                
                return redirect('products')
            else:
                return render(request, 'manager/create_product.html', {
                    'form': form
                })
        
        except ValueError:
            return render(request, 'manager/create_product.html', {
                'form': ProductForm(request.POST, request.FILES),
                'error': 'Por favor provee datos válidos'
            })

@login_required
def product_detail(request, products_id:int):
    # Obtenemos el producto (Solo si pertenece al usuario actual)
    producto = get_object_or_404(Producto, pk=products_id)

    if request.method == 'GET':
        form = ProductForm(instance=producto)
        # CAMBIO IMPORTANTE: Cambié 'productos' a 'product' para que coincida con tu HTML
        return render(request, 'manager/products_detail.html', {'product': producto, 'form': form}) 
    
    else:
        try:
            form = ProductForm(request.POST, request.FILES, instance=producto)
            if form.is_valid():
                form.save()

                # === LÓGICA PARA AGREGAR MÁS IMÁGENES AL EDITAR ===
                images = form.cleaned_data.get('imagenes_extra')
                if images:
                    for img in images:
                        ProductoImagen.objects.create(producto=producto, imagen=img)
                # ==================================================

                return redirect('products')
            else:
                return render(request, 'manager/products_detail.html', {
                    'product': producto, 
                    'form': form 
                })
        except ValueError:
            return render(request, 'manager/products_detail.html', {
                'product': producto, 
                'form': form, 
                'error': "Error updating product"
            })
    
def sent_product(request, products_id:int):
    # Productos enviados
    # Se asegura de obtener el producto SOLO si pertenece al usuario logueado
    producto = get_object_or_404(Producto, pk=products_id)
    if request.method == 'POST':
        # La condición se cumple: el producto existe y pertenece al usuario.
        # Se marca como 'enviado' (datecompleted)
        producto.datecompleted = timezone.now()
        producto.save()
        return redirect('products')


def delete_product(request, products_id:int):
    producto = get_object_or_404(Producto, pk=products_id)
    if request.method == 'POST':
        producto.delete()
        return redirect('products')

# ===============================================================================================================
# =================================== Productos verificados y por verificar ==============================
# ===============================================================================================================

def pagos_verificar(request):
    # ...
    ordenes_pendientes = OrdenDeCompra.objects.filter(estado='PENDIENTE').order_by('-fecha_orden')
    
    context = {
        'ordenes_pendientes': ordenes_pendientes,
        'sent_view': False # Indica que estamos en la vista de pendientes
    }
    return render(request, 'manager/pagos_verificar.html', context)


def pagos_aprovados(request):
    # ...
    ordenes_aprovadas = OrdenDeCompra.objects.filter(estado='APROBADA').order_by('-fecha_orden')
    
    context = {
        'ordenes_aprovadas': ordenes_aprovadas, # Las órdenes aprobadas
        'sent_view': True # Indica que estamos en la vista de aprobadas
    }
    return render(request, 'manager/pagos_verificar.html', context)

def pagos_rechazados(request):
    ordenes_rechazadas = OrdenDeCompra.objects.filter(estado='RECHAZADA').order_by('-fecha_orden')

    context = {
        'ordenes_rechazadas': ordenes_rechazadas,
        'orden_rechazar': True
    }
    return render(request, 'manager/pagos_verificar.html', context)
    

@login_required
@require_POST # Se recomienda usar POST para cambios de estado
def orden_aprobar(request, orden_id):
    """Marca una OrdenDeCompra como APROBADA."""
    orden = get_object_or_404(OrdenDeCompra, pk=orden_id)
    
    # Solo se puede aprobar si está PENDIENTE
    if orden.estado == 'PENDIENTE':
        orden.estado = 'APROBADA'
        orden.save()
        messages.success(request, f"La orden ID **{orden.id_compra}** ha sido APROBADA.")
    else:
        messages.error(request, f"La orden ID **{orden.id_compra}** ya está en estado {orden.estado}.")
        
    return redirect('pagos_verificar')

@login_required
@require_POST # Se recomienda usar POST para cambios de estado
def orden_rechazar(request, orden_id):
    """Marca una OrdenDeCompra como RECHAZADA y revierte el stock."""
    orden = get_object_or_404(OrdenDeCompra, pk=orden_id)
    
    if orden.estado == 'PENDIENTE':
        try:
            with transaction.atomic():
                # 1. Cambiar estado a RECHAZADA
                orden.estado = 'RECHAZADA'
                orden.save()
                
                # 2. Revertir el stock de todos los productos
                for item in orden.items_orden.all(): # type: ignore
                    producto = item.producto
                    producto.cantidad += item.cantidad # Devolver la cantidad al stock
                    producto.save()
                    
                messages.warning(request, f"La orden ID **{orden.id_compra}** ha sido RECHAZADA y el stock ha sido revertido.")
                
        except Exception as e:
            messages.error(request, f"Error al rechazar la orden y revertir stock: {str(e)}")
    else:
        messages.error(request, f"La orden ID **{orden.id_compra}** no puede ser rechazada. Estado actual: {orden.estado}.")
    
    return redirect('pagos_verificar')

# ========================================================================================================================================


# ===============================================================================================================
#===================================Triven ==================================================================
# ===============================================================================================================

def index(request):
    """Renderiza la página de inicio.

    Esta vista simplemente devuelve la plantilla 'home.html'.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que renderiza 'home.html'.
    """
    productos = Producto.objects.filter( datecompleted__isnull=False).order_by('-datecompleted')
    
    return render(request, 'index.html', {'productos': productos, 'sent_view': True})


def products_store(request):
    # 1. Obtener parámetros de filtro de la URL (GET request)
    category_code = request.GET.get('category')
    min_price_str = request.GET.get('min_price')
    max_price_str = request.GET.get('max_price')
    # NUEVO: Obtener el término de búsqueda
    search_query = request.GET.get('q') # Usaremos 'q' como nombre del parámetro de búsqueda
    
    # 2. Inicializar el queryset base
    productos_queryset = Producto.objects.filter(datecompleted__isnull=False)

    # NUEVO: 3. Aplicar filtro de BÚSQUEDA por título
    if search_query:
        # Filtra productos cuyo título contenga (insensible a mayúsculas/minúsculas) el término de búsqueda
        productos_queryset = productos_queryset.filter(title__icontains=search_query)

    # 4. Aplicar filtro de CATEGORÍA (Mantenemos la numeración del código original)
    if category_code:
        productos_queryset = productos_queryset.filter(category=category_code)

    # 5. Aplicar filtro de PRECIO
    
    # Conversión segura del precio mínimo
    if min_price_str and min_price_str.isdigit():
        min_price = Decimal(min_price_str)
        productos_queryset = productos_queryset.filter(price__gte=min_price)
    else:
        min_price = None

    # Conversión segura del precio máximo
    if max_price_str and max_price_str.isdigit():
        max_price = Decimal(max_price_str)
        productos_queryset = productos_queryset.filter(price__lte=max_price)
    else:
        max_price = None
        
    # 6. Ordenar el queryset final y obtener la cantidad
    productos = productos_queryset.order_by('-datecompleted')
    numero_productos = productos.count()

    # ... (código de tasa de bolívar - lo mantienes igual) ...
    bolivar_rate = get_exchange_rate()

    if bolivar_rate is not None:
        bolivar_rate = Decimal(str(bolivar_rate)) 

    for producto in productos:
        if bolivar_rate is not None:
            conversion = producto.price * bolivar_rate
            producto.price_ves = conversion # pyright: ignore[reportAttributeAccessIssue]
        else:
            producto.price_ves = None # pyright: ignore[reportAttributeAccessIssue]

    # 7. Retornar los datos filtrados y los valores activos
    return render(request, 'tienda.html',
    {
        'productos': productos,
        'sent_view': True,
        'cantidad': numero_productos,
        'bolivar_rate': bolivar_rate, # Asume que 'bolivar_rate' se calcula arriba
        'categorias': CATEGORIA_CHOICES, # Asume que 'CATEGORIA_CHOICES' está definido
        'current_category': category_code,
        'min_price': min_price,
        'max_price': max_price,
        # NUEVO: Pasar el término de búsqueda actual al template para rellenar la barra
        'search_query': search_query,
    })
# ===============================================================================================================
# =================================== Lógica del Carrito =======================================================
# ===============================================================================================================

@login_required
@login_required
def add_to_cart(request):
    """Agrega un producto al carrito (sesión). Soporta adición de cantidad, restringida por stock."""
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        try:
            # Cantidad que el usuario intenta agregar
            cantidad_a_agregar = int(request.POST.get('cantidad', 1)) 
            if cantidad_a_agregar < 1:
                cantidad_a_agregar = 1
        except ValueError:
            cantidad_a_agregar = 1

        producto = get_object_or_404(Producto, pk=producto_id, datecompleted__isnull=False)
        
        # Obtener el carrito de la sesión
        cart = request.session.get('cart', {})
        producto_id_str = str(producto_id)
        
        # Stock disponible (Asumimos que el modelo tiene el campo 'stock')
        stock_disponible = producto.cantidad

        cantidad_actual_en_carrito = cart.get(producto_id_str, {}).get('cantidad', 0)
        nueva_cantidad_total = cantidad_actual_en_carrito + cantidad_a_agregar

        # Validar si la nueva cantidad total excede el stock
        if nueva_cantidad_total > stock_disponible:
            # La cantidad a agregar se ajusta al máximo permitido
            cantidad_permitida = stock_disponible - cantidad_actual_en_carrito
            
            if cantidad_permitida > 0:
                # Agrega solo lo que falta para llegar al límite del stock
                cart[producto_id_str]['cantidad'] = stock_disponible
                messages.warning(request, f"Solo se han añadido {cantidad_permitida} unidades de {producto.title}. El stock máximo es de {stock_disponible}.")
            else:
                # Si la cantidad actual ya es mayor o igual al stock, no se añade nada
                messages.error(request, f"No puedes añadir más unidades de {producto.title}. Ya tienes el stock máximo ({stock_disponible}) en tu carrito.")
                return redirect('tienda') # Permite que el usuario vea el mensaje en la tienda
        else:
            # Actualiza o añade el producto
            if producto_id_str in cart:
                cart[producto_id_str]['cantidad'] += cantidad_a_agregar
            else:
                cart[producto_id_str] = {
                    'id': producto.id,  # type: ignore
                    'title': producto.title,
                    'price': float(producto.price),
                    'imagen_url': producto.imagen.url,
                    'cantidad': cantidad_a_agregar,
                    # IMPORTANTE: Almacenar el stock para validaciones futuras en el carrito
                    'stock': stock_disponible, 
                }
            messages.success(request, f"{cantidad_a_agregar} unidades de {producto.title} añadidas al carrito.")

        request.session['cart'] = cart
        request.session.modified = True
        return redirect('carrito') 
    return redirect('tienda')

@login_required
def remove_from_cart(request, producto_id):
    """Elimina un producto por completo del carrito (sesión)."""
    cart = request.session.get('cart', {})
    
    # Convierte el ID a string, ya que las claves de sesión son strings
    producto_id_str = str(producto_id)
    
    if producto_id_str in cart:
        del cart[producto_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('carrito')

@login_required
def update_cart_quantity(request, producto_id):
    """Actualiza la cantidad de un producto específico en el carrito, restringida por stock."""
    if request.method == 'POST':
        producto_id_str = str(producto_id)
        try:
            new_quantity = int(request.POST.get('cantidad'))
        except (TypeError, ValueError):
            messages.error(request, "Cantidad inválida.")
            return redirect('carrito')

        if new_quantity < 1:
            new_quantity = 1 # Mínimo 1

        cart = request.session.get('cart', {})
        
        if producto_id_str in cart:
            producto = get_object_or_404(Producto, pk=producto_id, datecompleted__isnull=False)
            stock_disponible = producto.cantidad # Obtener el stock real de la DB

            if new_quantity > stock_disponible:
                # Si la cantidad nueva excede el stock, se ajusta al máximo (stock)
                messages.error(request, f"La cantidad máxima para {producto.title} es {stock_disponible}. Cantidad ajustada.")
                new_quantity = stock_disponible
                
            if new_quantity > 0:
                cart[producto_id_str]['cantidad'] = new_quantity
                # Opcional: actualizar el stock también si hubo una actualización en la tienda
                cart[producto_id_str]['stock'] = stock_disponible 
                request.session['cart'] = cart
                request.session.modified = True
        else:
             messages.error(request, "Producto no encontrado en el carrito.")

    return redirect('carrito')

@login_required
def clear_cart(request):
    """Elimina todos los items del carrito."""
    if request.method == 'POST':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
    return redirect('carrito')


def carrito(request):
    """Muestra el contenido del carrito, incluyendo la conversión a Bolívares y el stock disponible."""
    cart = request.session.get('cart', {})
    items = []
    subtotal_usd = Decimal(0.00)
    
    # Obtener la tasa de cambio
    bolivar_rate_float = get_exchange_rate()
    if bolivar_rate_float is not None:
        bolivar_rate = Decimal(str(bolivar_rate_float))
    else:
        bolivar_rate = None

    # Obtener IDs de productos para una consulta eficiente
    producto_ids = [int(id_str) for id_str in cart.keys()]
    
    # Obtener productos y su stock de la base de datos en una sola consulta
    productos_db = Producto.objects.filter(id__in=producto_ids).values('id', 'cantidad', 'title') 
    stock_map = {item['id']: item['cantidad'] for item in productos_db}


    for producto_id_str, data in cart.items():
        producto_id = int(producto_id_str)
        stock_disponible = stock_map.get(producto_id, 0) # 0 si no se encuentra (producto eliminado/inactivo)
        
        cantidad = data.get('cantidad', 1)
        price_usd = Decimal(str(data.get('price', 0.00)))
        total_item_usd = price_usd * cantidad
        subtotal_usd += total_item_usd
        price_ves = None
        total_item_ves = None

        if bolivar_rate:
            price_ves = price_usd * bolivar_rate
            total_item_ves = total_item_usd * bolivar_rate
            
        # IMPORTANTE: Revisar si la cantidad actual supera el stock (por si el stock cambió después de añadirlo)
        if cantidad > stock_disponible:
             # Opcional: Ajustar la cantidad en el carrito automáticamente
             data['cantidad'] = stock_disponible
             request.session.modified = True
             cantidad = stock_disponible # Usar la cantidad ajustada
             messages.warning(request, f"La cantidad de **{data.get('title')}** se ajustó a su stock máximo de {stock_disponible}.")
             
        # Si el stock es 0, no mostrarlo o mostrarlo como no disponible (aquí se mantendrá el item)
        if stock_disponible == 0:
            messages.error(request, f"**{data.get('title')}** no está disponible temporalmente. Por favor, elimínalo.")


        items.append({
            'producto_id': producto_id,
            'title': data.get('title'),
            'price_usd': price_usd,
            'price_ves': price_ves,
            'cantidad': cantidad,
            'imagen_url': data.get('imagen_url'),
            'total_item_usd': total_item_usd,
            'total_item_ves': total_item_ves,
            'max_stock': stock_disponible, # <--- ¡NUEVO! Stock máximo para el template
        })

    subtotal_ves = subtotal_usd * bolivar_rate if bolivar_rate else None
    
    context = {
        'items': items,
        'subtotal_usd': subtotal_usd,
        'subtotal_ves': subtotal_ves,
        'bolivar_rate': bolivar_rate,
    }
    return render(request, 'carrito.html', context)

# ===============================================================================================================
# =================================== Lógica de Pago/Compra (Con ID Único y Stock) ==============================
# ===============================================================================================================
@login_required
def compra_productos(request):
    """Maneja el formulario de pago, genera el ID único, registra la orden y reduce el stock."""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.error(request, "Tu carrito está vacío. No puedes proceder al pago.")
        return redirect('carrito')

    # --- Generación del ID Único (GET/POST) ---
    # Usar un ID de 8 caracteres alfanumérico. 
    if 'id_compra' not in request.session:
        # Generar un UUID, tomar los primeros 8 caracteres y hacerlo mayúsculas.
        unique_id = uuid.uuid4().hex[:8].upper()
        request.session['id_compra'] = unique_id
    
    id_compra_actual = request.session['id_compra']

    # --- LÓGICA POST: Procesar el pago y comprobante ---
    if request.method == 'POST':
        id_confirmacion = request.POST.get('id_confirmacion')
        imagen_comprobante = request.FILES.get('imagen_comprobante')

        if str(id_confirmacion).strip() != id_compra_actual:
            messages.error(request, "El ID de compra confirmado no coincide con el asignado. Inténtalo de nuevo.")
            return redirect('compra_productos')
        
        if not imagen_comprobante:
            messages.error(request, "Debe adjuntar la imagen del comprobante de pago.")
            return redirect('compra_productos')
            
        try:
            total_orden_usd = Decimal(0.00)
            items_detalle = []
            
            # Usar una transacción atómica para asegurar que la orden se crea
            # y el stock se reduce, o se revierte todo.
            with transaction.atomic():
                
                # 1. Crear la Orden de Compra Inicial
                orden = OrdenDeCompra.objects.create(
                    user=request.user,
                    id_compra=id_compra_actual,
                    subtotal_usd=Decimal(0.00), 
                    estado='PENDIENTE' 
                )

                # 2. Recorrer el carrito, reducir stock y crear ItemOrden
                for producto_id_str, data in cart.items():
                    producto_id = int(producto_id_str)
                    cantidad_comprada = data.get('cantidad', 1)
                    precio_unidad = Decimal(str(data.get('price', 0.00)))
                    
                    producto = Producto.objects.select_for_update().get(pk=producto_id)
                    
                    # Validación Final de Stock
                    if producto.cantidad < cantidad_comprada:
                        raise Exception(f"Stock insuficiente para **{producto.title}**. Solo quedan {producto.cantidad}.")

                    # **REDUCCIÓN DE STOCK**
                    producto.cantidad -= cantidad_comprada
                    producto.save()

                    # Crear el Item de la Orden
                    ItemOrden.objects.create( 
                        orden=orden,
                        producto=producto,
                        cantidad=cantidad_comprada,
                        precio_unidad=precio_unidad,

                        nombre_producto_snapshot=producto.title,descripcion_snapshot=producto.description,
                    )
                    
                    total_item_usd = precio_unidad * cantidad_comprada
                    total_orden_usd += total_item_usd
                    
                    items_detalle.append({
                        'title': producto.title,
                        'cantidad': cantidad_comprada,
                        'precio_unidad': precio_unidad
                    })

                # 3. Guardar Comprobante y Total en la Orden
                orden.subtotal_usd = total_orden_usd
                orden.imagen_comprobante.save(
                    f'comprobante_{id_compra_actual}.{imagen_comprobante.name.split(".")[-1]}', 
                    imagen_comprobante
                )
                orden.save()

            # 4. Generar Enlace de WhatsApp con datos de la factura
            # **IMPORTANTE**: No es posible adjuntar archivos (como el PDF) directamente 
            # a través del enlace estándar de WhatsApp API/Web. Solo se puede enviar texto.
            
            # Número de teléfono de destino (Ejemplo: +584120000000)
            whatsapp_number = "584121834638" 
            
            message = (
                f"¡Nueva Orden de Compra (Validación)!\n"
                f"ID de Compra: *{id_compra_actual}*\n"
                f"Cliente: {request.user.username}\n"
                f"Total Pagado: ${total_orden_usd:.2f}\n"
                f"Productos:\n"
            )
            for item in items_detalle:
                message += f"  - {item['title']} x{item['cantidad']} (${(item['precio_unidad'] * item['cantidad']):.2f})\n"
            
            message += "\n*Adjunté el capture del pago a esta conversación.*"
            
            encoded_message = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
            
            # 5. Limpiar sesión y mostrar éxito
            # Si la transacción fue exitosa, borramos el carrito y el ID de sesión
            del request.session['cart']
            del request.session['id_compra']
            request.session.modified = True
            
            messages.success(request, f"¡Pago registrado! ID: **{id_compra_actual}**. Serás redirigido para enviar el comprobante por WhatsApp.")
            
            return redirect(whatsapp_url)

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {str(e)}. La compra no se ha completado y el stock no se redujo.")
            # Si falla, el carrito y el ID de compra siguen en la sesión
            return redirect('compra_productos')


    # --- LÓGICA GET: Mostrar el formulario con el ID generado ---
    context = {
        'id_compra': id_compra_actual,
    }
    return render(request, 'pago.html', context)



#=================================================================================================================================



@login_required
def user_details(request):
    # Cargar las órdenes que irán en la pestaña 'Por Verificar' (PENDIENTE)
    ordenes_pendientes = OrdenDeCompra.objects.filter(
        estado='PENDIENTE',
        user=request.user # Asegúrate de usar 'user' si ese es el nombre de la FK en OrdenDeCompra
    ).order_by('-fecha_orden')
    
    # También puedes cargar las otras listas, aunque no se usen hasta que se haga clic en la pestaña
    # (Esto puede ser ineficiente si las listas son muy grandes, pero simplifica el template)
    ordenes_aprobadas = OrdenDeCompra.objects.filter(
        estado='APROBADA',
        user=request.user
    ).order_by('-fecha_orden')

    ordenes_rechazadas = OrdenDeCompra.objects.filter(
        estado='RECHAZADA',
        user=request.user
    ).order_by('-fecha_orden')

    contexto = {
        'username': request.user.username,
        # Variables de contexto para el template
        'ordenes_pendientes': ordenes_pendientes,
        'ordenes_aprobadas': ordenes_aprobadas,
        'ordenes_rechazadas': ordenes_rechazadas,
        # Sent_view se puede omitir o manejar de otra forma en el HTML
        'sent_view': False # Default para la pestaña Por Verificar
    }

    return render(request, 'user_detail.html', contexto)

@login_required
def products_items(request, products_id:int):
    producto = get_object_or_404(
        Producto, 
        pk=products_id, 
        datecompleted__isnull=False # Asegura que solo se muestren productos 'enviados' (a la venta)
    )

    # Recuperamos las imágenes extra usando el related_name 'imagenes_galeria'
    imagenes_extra = producto.imagenes_galeria.all() # type: ignore
    
    # Aquí puedes añadir la lógica de conversión a Bs. si es necesaria, 
    bolivar_rate = get_exchange_rate()

    if bolivar_rate is not None:
        bolivar_rate = Decimal(str(bolivar_rate)) 

        if bolivar_rate is not None:
            conversion = producto.price * bolivar_rate
            producto.price_ves = conversion # pyright: ignore[reportAttributeAccessIssue]
        else:
            producto.price_ves = None # pyright: ignore[reportAttributeAccessIssue]
    # pero para simplificar, la dejaremos solo en la lista por ahora.
    
    return render(request, 'products_items.html', {'producto': producto, 'bolivar_rate': bolivar_rate,'imagenes_galeria': imagenes_extra })

def signup(request):
    """Gestiona el registro de nuevos usuarios con validaciones extendidas."""
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password_1 = request.POST.get('password1')
        password_2 = request.POST.get('password2')
        
        # 1. Chequeo de que las contraseñas coincidan
        if password_1 != password_2:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': "Error: Las contraseñas no coinciden."
            })

        # 2. Chequeo de que la contraseña no sea la misma que el username (Buena Práctica)
        if password_1 == username:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': "Error: La contraseña no puede ser igual al nombre de usuario."
            })

        # 3. Chequeo de unicidad de Email
        # Django no garantiza email unique por defecto, lo comprobamos manualmente
        if email and User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': "Error: El correo electrónico ya está registrado."
            })
            
        # 4. Creación del usuario
        try:
            # user.save() es implícito en create_user si se usa Manager
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password_1
            )
            login(request, user)
            return redirect('tienda')
            
        except IntegrityError:
            # Esto atrapará el error de un nombre de usuario duplicado
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': "Error: El nombre de usuario ya está registrado."
            })
    
@login_required
def signout(request):
    logout(request)
    return redirect('index')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
        'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'User or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tienda')
        
