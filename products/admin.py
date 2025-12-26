from django.contrib import admin
from .models import *# <--- Importa el nuevo modelo
from django.utils.html import format_html # <-- ¡Añade esta línea!

# Esto permite editar las imágenes DENTRO de la página del producto
class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1  # Cuántos campos vacíos mostrar por defecto
    can_delete = True 
    readonly_fields = ('ver_miniatura',)

    def ver_miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.imagen.url)
        return "Sin imagen"
    ver_miniatura.short_description = "Miniatura"

class ProductoAdmin(admin.ModelAdmin):
    # Agregamos el inline al admin del producto
    inlines = [ProductoImagenInline] 
    list_display = ('title', 'user', 'price', 'created', 'ver_portada')

    readonly_fields = ('portada_preview',)

    def ver_portada(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="40" height="40" />', obj.imagen.url)
        return "-"
    
    def portada_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="200" />', obj.imagen.url)
        return "No hay imagen de portada"
    
    # Organizamos los campos para que la gestión sea clara
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'user', 'category', 'price', 'cantidad')
        }),
        ('Imagen de Portada', {
            'fields': ('imagen', 'portada_preview'),
            'description': 'Marca el checkbox "Eliminar" al lado de la imagen actual para quitarla sin borrar el producto.'
        }),
    )

admin.site.register(Producto, ProductoAdmin)

# ==============================================================================
# 2. Admin para Órdenes de Compra
# ==============================================================================

# Permite ver y editar los ítems DENTRO de la página de la orden
class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0 # No queremos campos vacíos, solo mostrar los existentes
    # Campos de solo lectura para la instantánea
    readonly_fields = ('nombre_producto_snapshot', 'descripcion_snapshot', 'cantidad', 'precio_unidad', 'total_item')
    fields = ('producto', 'nombre_producto_snapshot', 'descripcion_snapshot', 'cantidad', 'precio_unidad', 'total_item')
    can_delete = False # No es recomendable borrar ítems de una orden ya hecha

class OrdenDeCompraAdmin(admin.ModelAdmin):
    inlines = [ItemOrdenInline] # Agregamos los ítems
    list_display = ('id_compra', 'user', 'fecha_orden', 'subtotal_usd', 'estado', 'nota_manager')
    list_filter = ('estado', 'fecha_orden')
    search_fields = ('id_compra', 'user__username')
    readonly_fields = ('id_compra', 'fecha_orden', 'subtotal_usd', 'imagen_comprobante_tag') # Estos no deben ser editables
    
    # Campo personalizado para mostrar la imagen del comprobante en el admin
    # Necesitas importar format_html si vas a usar esta función
    from django.utils.html import format_html 
    def imagen_comprobante_tag(self, obj):
        if obj.imagen_comprobante:
            # Crea un enlace a la imagen y muestra un thumbnail
            return format_html('<a href="{}" target="_blank"><img src="{}" width="150" /></a>', obj.imagen_comprobante.url, obj.imagen_comprobante.url)
        return "No hay comprobante"
    imagen_comprobante_tag.short_description = 'Comprobante de Pago'
    
    # El orden de los campos en la vista de detalle
    fieldsets = (
        (None, {
            'fields': ('user', 'id_compra', 'fecha_orden', 'subtotal_usd', 'estado', 'nota_manager')
        }),
        ('Detalle de Pago', {
            'fields': ('imagen_comprobante_tag', 'imagen_comprobante')
        }),
    )

# Registramos la Orden de Compra
admin.site.register(OrdenDeCompra, OrdenDeCompraAdmin)


# ==============================================================================
# 3. Admin para Carrito (Opcional, pero útil)
# ==============================================================================

# Inline para ver los ítems dentro del carrito
class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0
    readonly_fields = ('fecha_añadido', 'total_item')
    fields = ('producto', 'cantidad', 'precio_unidad', 'total_item', 'fecha_añadido')

class CarritoAdmin(admin.ModelAdmin):
    inlines = [ItemCarritoInline]
    list_display = ('user', 'fecha_creacion')
    readonly_fields = ('fecha_creacion',)

# Registramos el Carrito
admin.site.register(Carrito, CarritoAdmin)