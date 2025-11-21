from django.contrib import admin
from .models import Producto, ProductoImagen # <--- Importa el nuevo modelo

# Esto permite editar las imágenes DENTRO de la página del producto
class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1  # Cuántos campos vacíos mostrar por defecto

class ProductoAdmin(admin.ModelAdmin):
    # Agregamos el inline al admin del producto
    inlines = [ProductoImagenInline] 
    list_display = ('title', 'user', 'price', 'created')

# Registramos el modelo principal con su configuración personalizada
admin.site.register(Producto, ProductoAdmin)

# Si tenías registrado Producto antes, asegúrate de borrar la línea vieja o sobrescribirla con esta lógica.