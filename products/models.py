from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver


CATEGORIA_CHOICES = (
    ('SALUD', 'Salud y Belleza'),
    ('HIGIENE', 'Higiene'),
    ('COMESTIBLES', 'Comestibles'),
    ('OTROS', 'Otros'),
)



class Producto(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cantidad = models.IntegerField(default=1)
    
    # Esta sigue siendo tu IMAGEN PRINCIPAL para la tienda.html
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    
    datecompleted = models.DateTimeField(null=True, blank=True)
    category = models.CharField(max_length=11, choices=CATEGORIA_CHOICES, default="OTROS")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + '- by ' + self.user.username

# === NUEVO MODELO PARA LA GALERÍA ===
class ProductoImagen(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes_galeria')
    imagen = models.ImageField(upload_to='productos_galeria/')
    
    def __str__(self):
        return f"Imagen extra de {self.producto.title}"

# ================================ NUEVOS MODELOS PARA LA ORDEN DE COMPRA ================================

class OrdenDeCompra(models.Model):
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    )
    
    # Campo nuevo para la nota del manager
    nota_manager = models.TextField(
        null=True, 
        blank=True, 
        verbose_name="Nota del Manager"
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ID único y aleatorio para referenciar el pago
    id_compra = models.CharField(max_length=100, unique=True) 
    fecha_orden = models.DateTimeField(auto_now_add=True)
    subtotal_usd = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    # Campo para el comprobante (capture de pago móvil)
    imagen_comprobante = models.ImageField(upload_to='comprobantes/', null=True, blank=True)
    
    def __str__(self):
        return f"Orden {self.id_compra} de {self.user.username}"


class ItemOrden(models.Model):
    orden = models.ForeignKey(OrdenDeCompra, on_delete=models.CASCADE, related_name='items_orden')
    
    # ----------------------------------------------------
    # CAMBIO CRÍTICO: Usar SET_NULL y null=True
    # Si el producto se elimina, el item de la orden se queda, pero el FK es NULL
    # ----------------------------------------------------
    producto = models.ForeignKey(
        'Producto', 
        on_delete=models.SET_NULL, # Se pone a NULL si Producto es borrado
        null=True, # Permite que sea NULL
        blank=True # Permite que sea NULL en formularios
    )  
    
    # CAMPOS DE INSTANTÁNEA (Snapshot): Para que la orden mantenga la información
    # esencial aunque el producto original se borre.
    nombre_producto_snapshot = models.CharField(max_length=100, default='Producto Eliminado')
    descripcion_snapshot = models.TextField(blank=True, null=True)
    
    # El resto de campos se mantiene:
    cantidad = models.PositiveIntegerField(default=1)
    precio_unidad = models.DecimalField(max_digits=6, decimal_places=2) # Precio al momento de la compra
    
    def total_item(self):
        # Asegúrate de usar el precio de la instantánea (precio_unidad)
        return self.precio_unidad * self.cantidad

    def __str__(self):
        # Usamos el nombre de la instantánea para el __str__
        return f"{self.cantidad} x {self.nombre_producto_snapshot} en Orden {self.orden.id_compra}"


# ================================ NUEVOS MODELOS PARA EL CARRITO ================================

class Carrito(models.Model):
    # El carrito se asocia a un usuario. Si es anónimo, podrías usar la sesión de Django.
    # Para este ejemplo, asumiremos un usuario autenticado por simplicidad con un carrito persistente.
    # Si quieres un carrito de sesión, la lógica es diferente (usar la sesión de Django).
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Carrito de {self.user.username}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    # Almacenar el precio al momento de añadir para evitar problemas si el precio del producto cambia
    precio_unidad = models.DecimalField(max_digits=6, decimal_places=2) 
    fecha_añadido = models.DateTimeField(auto_now_add=True)

    def total_item(self):
        return self.precio_unidad * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.title} en el carrito de {self.carrito.user.username}"

# Señal para asegurar que se cree un carrito para cada nuevo usuario
@receiver(pre_save, sender=User)
def create_user_carrito(sender, instance, **kwargs):
    if instance._state.adding: # Solo si el usuario es nuevo
        # Carrito.objects.get_or_create(user=instance) # Mejor hacerlo en el post_save para asegurar que el User exista
        pass

# Usaremos post_save para asegurar que el usuario ya existe en la base de datos
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def create_user_carrito_post_save(sender, instance, created, **kwargs):
    if created:
        Carrito.objects.get_or_create(user=instance)

# =================================================================================================