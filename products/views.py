from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import ProductForm
from .serializers import ItemSerializer
from .models import Producto, CATEGORIA_CHOICES, Carrito, ItemCarrito # <--- IMPORTANTE: Importar Carrito e ItemCarrito
from django.contrib import messages
from.conversion import get_exchange_rate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal
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
    productos = Producto.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'manager/products.html', {'productos': productos , 'sent_view': False})

@login_required
def products_to_send(request):
    productos = Producto.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'manager/products.html', {'productos': productos, 'sent_view': True})

@login_required
def create_product(request):
    if request.method == 'GET':
        return render(request, 'manager/create_product.html', {
            'form': ProductForm
        })
    else:
        try:
            form = ProductForm(request.POST)
            new_product = form.save(commit=False)
            new_product.user = request.user
            new_product.save()
            return redirect('products')
        
        except ValueError:
            return render(request, 'manager/create_product.html', {
                'form': ProductForm,
                'error': 'Porfavor provide valida data'
            })

@login_required
def product_detail(request, products_id:int):
    if request.method == 'GET':
        producto = get_object_or_404(Producto, pk=products_id, user=request.user)
        form = ProductForm(instance=producto)
        return render(request, 'manager/products_detail.html', {'productos': producto, 'form': form})
    else:
        try:
            producto = get_object_or_404(Producto, pk=products_id, user=request.user)
            form = ProductForm(request.POST, instance=producto)
            form.save()
            return redirect('products')
        except ValueError:
            return render(request, 'manager/products_detail.html', {'productos': producto, 'form': form, 'error': "Error updating product"})

def sent_product(request, products_id:int):
    # Productos enviados
    # Se asegura de obtener el producto SOLO si pertenece al usuario logueado
    producto = get_object_or_404(Producto, pk=products_id, user=request.user)
    if request.method == 'POST':
        # La condición se cumple: el producto existe y pertenece al usuario.
        # Se marca como 'enviado' (datecompleted)
        producto.datecompleted = timezone.now()
        producto.save()
        return redirect('products')


def delete_product(request, products_id:int):
    producto = get_object_or_404(Producto, pk=products_id, user=request.user)
    if request.method == 'POST':
        producto.delete()
        return redirect('products')

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
    min_price_str = request.GET.get('min_price') # Nuevo: Precio Mínimo
    max_price_str = request.GET.get('max_price') # Nuevo: Precio Máximo
    
    # 2. Inicializar el queryset base
    productos_queryset = Producto.objects.filter(datecompleted__isnull=False)

    # 3. Aplicar filtro de CATEGORÍA
    # Nota: Usaremos 'categoria' en el filtro de Django para coincidir con el error que tenías,
    # que indica que ese es el nombre del campo en tu modelo/DB.
    if category_code:
        productos_queryset = productos_queryset.filter(category=category_code)

    # 4. Aplicar filtro de PRECIO
    
    # Conversión segura del precio mínimo
    if min_price_str and min_price_str.isdigit():
        min_price = Decimal(min_price_str)
        # Filtra productos donde el 'price' sea mayor o igual al mínimo
        productos_queryset = productos_queryset.filter(price__gte=min_price)
    else:
        min_price = None

    # Conversión segura del precio máximo
    if max_price_str and max_price_str.isdigit():
        max_price = Decimal(max_price_str)
        # Filtra productos donde el 'price' sea menor o igual al máximo
        productos_queryset = productos_queryset.filter(price__lte=max_price)
    else:
        max_price = None
        
    # 5. Ordenar el queryset final y obtener la cantidad
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

    # 6. Retornar los datos filtrados y los valores activos para rellenar el formulario
    return render(request, 'tienda.html',
    {
        'productos': productos,
        'sent_view': True,
        'cantidad': numero_productos,
        'bolivar_rate': bolivar_rate,
        'categorias': CATEGORIA_CHOICES,
        'current_category': category_code, # Usado para la categoría activa
        'min_price': min_price,           # Nuevo: Usado para rellenar el input de precio mínimo
        'max_price': max_price            # Nuevo: Usado para rellenar el input de precio máximo
    })
# ===============================================================================================================
# =================================== Lógica del Carrito =======================================================
# ===============================================================================================================

@login_required
def add_to_cart(request):
    """Agrega un producto al carrito (sesión). Soporta adición de cantidad."""
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        try:
            cantidad = int(request.POST.get('cantidad', 1)) # Obtener cantidad, por defecto 1
            if cantidad < 1:
                cantidad = 1
        except ValueError:
            cantidad = 1

        producto = get_object_or_404(Producto, pk=producto_id, datecompleted__isnull=False)
        
        # Inicializa el carrito si no existe en la sesión
        cart = request.session.get('cart', {})
        
        # Usa el ID del producto como clave.
        if producto_id in cart:
            # Si ya existe, actualiza la cantidad (sumando la nueva cantidad)
            # Esto puede ser una simple suma o reemplazar, dependiendo de si el formulario permite elegir una nueva.
            # Aquí, lo sumamos para la tienda, o lo establecemos si viene de un lugar que define la cantidad total.
            
            # NOTA: Para la tienda, la mejor práctica es AÑADIR. 
            # Para la página de detalle/carrito, se puede REEMPLAZAR.
            # Para simplicidad, aquí lo SUMAMOS:
            cart[producto_id]['cantidad'] += cantidad
        else:
            # Si no existe, lo agrega.
            cart[producto_id] = {
                'id': producto.id, # type: ignore
                'title': producto.title,
                'price': float(producto.price), # Guardar como float o str para serialización en sesión
                'imagen_url': producto.imagen.url,
                'cantidad': cantidad
            }

        request.session['cart'] = cart
        request.session.modified = True
        return redirect('carrito') # Redirige al carrito después de agregar
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
    """Actualiza la cantidad de un producto específico en el carrito."""
    if request.method == 'POST':
        producto_id_str = str(producto_id)
        try:
            # Asegúrate de que la cantidad es válida
            new_quantity = int(request.POST.get('cantidad'))
            if new_quantity < 1:
                new_quantity = 1
        except (TypeError, ValueError):
            return redirect('carrito') # O muestra un error

        cart = request.session.get('cart', {})
        
        if producto_id_str in cart:
            cart[producto_id_str]['cantidad'] = new_quantity
            request.session['cart'] = cart
            request.session.modified = True

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
    """Muestra el contenido del carrito, incluyendo la conversión a Bolívares."""
    cart = request.session.get('cart', {})
    items = []
    subtotal_usd = Decimal(0.00)
    
    # Obtener la tasa de cambio
    bolivar_rate_float = get_exchange_rate()
    if bolivar_rate_float is not None:
        bolivar_rate = Decimal(str(bolivar_rate_float))
    else:
        bolivar_rate = None # O usar un valor por defecto si la API falla (ej: Decimal(0.00))

    # Recalcular el subtotal y preparar los datos para la plantilla
    for producto_id_str, data in cart.items():
        cantidad = data.get('cantidad', 1)
        price_usd = Decimal(str(data.get('price', 0.00)))
        total_item_usd = price_usd * cantidad
        subtotal_usd += total_item_usd
        
        # Lógica de conversión a Bolívares
        price_ves = None
        total_item_ves = None

        if bolivar_rate:
            price_ves = price_usd * bolivar_rate
            total_item_ves = total_item_usd * bolivar_rate

        items.append({
            'producto_id': int(producto_id_str),
            'title': data.get('title'),
            'price_usd': price_usd,
            'price_ves': price_ves,
            'cantidad': cantidad,
            'imagen_url': data.get('imagen_url'),
            'total_item_usd': total_item_usd,
            'total_item_ves': total_item_ves,
        })

    # Calcular subtotal total en Bolívares
    subtotal_ves = subtotal_usd * bolivar_rate if bolivar_rate else None
    
    context = {
        'items': items,
        'subtotal_usd': subtotal_usd,
        'subtotal_ves': subtotal_ves,
        'bolivar_rate': bolivar_rate,
    }
    return render(request, 'carrito.html', context)

#=================================================================================================================================

@login_required
def user_details(request):
    username = request.user.username

    contexto = {
        'username': username
    }

    return render(request, 'user_detail.html', contexto)

@login_required
def products_items(request, products_id:int):
    producto = get_object_or_404(
        Producto, 
        pk=products_id, 
        datecompleted__isnull=False # Asegura que solo se muestren productos 'enviados' (a la venta)
    )
    
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
    
    return render(request, 'products_items.html', {'producto': producto, 'bolivar_rate': bolivar_rate})

def signup(request):
    """Gestiona el registro de nuevos usuarios.

    Si es una solicitud GET, muestra el formulario de registro.
    Si es una solicitud POST, intenta crear un nuevo usuario y, si tiene éxito,
    inicia la sesión del usuario y lo redirige a la lista de tareas.
    Maneja errores si las contraseñas no coinciden o si el nombre de usuario
    ya existe.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que:
        - Renderiza 'signup.html' con el formulario (GET).
        - Redirige a 'tienda' (POST exitoso).
        - Renderiza 'signup.html' con el formulario y un mensaje de error (POST fallido).
    """
    if request.method == 'GET':
        # Nota: Estamos usando UserCreationForm, pero si queremos un campo de email requerido
        # debemos crear un formulario personalizado (ProductUserCreationForm).
        # Para simplificar y usar solo el campo email *adicional*, modificaremos el POST.
        # Sin embargo, lo ideal es crear un formulario personalizado para validación.
        return render(request, 'signup.html', {
            'form': UserCreationForm # Podrías cambiar esto a un formulario personalizado si requieres validación estricta de email
        })
    else:
        # **CAMBIO CLAVE AQUÍ**
        # 1. Obtener el email del POST.
        # 2. Pasarlo a User.objects.create_user.
        if request.POST['password1'] == request.POST['password2']:
            try:
                # El campo 'email' está disponible en el request.POST ya que lo añadiremos en el HTML
                user = User.objects.create_user(
                    username=request.POST['username'],
                    email=request.POST['email'],  # <--- AÑADIDO: El campo email
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('tienda')
            
            except IntegrityError:
                # La integridad puede fallar por username duplicado (y ahora por email duplicado si lo haces unique)
                return render(request, 'signup.html', {
                    'form': UserCreationForm, # El formulario que se renderizará en caso de error
                    'error': "User alredy exists or email is already registered"
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm, # El formulario que se renderizará en caso de error
            'error': "Password do not match"
        })
    
@login_required
def signout(request):
    """Cierra la sesión del usuario actual y redirige a la página de inicio.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que redirige a 'home'.
    """
    logout(request)
    return redirect('index')


def signin(request):
    """Gestiona el inicio de sesión del usuario.

    Si es una solicitud GET, muestra el formulario de autenticación.
    Si es una solicitud POST, intenta autenticar al usuario. Si tiene éxito,
    inicia la sesión del usuario y lo redirige a la lista de tareas. Si falla,
    muestra un mensaje de error.

    Args:
        request: El objeto HttpRequest entrante.

    Returns:
        Un objeto HttpResponse que:
        - Renderiza 'signin.html' con el formulario (GET).
        - Redirige a 'products' (POST exitoso).
        - Renderiza 'signin.html' con el formulario y un mensaje de error (POST fallido).
    """

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
        
