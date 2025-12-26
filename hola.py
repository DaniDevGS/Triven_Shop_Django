# admin.py
from django.contrib import admin
from .models import *
from django.utils.html import format_html

class ProductoImagenInline(admin.TabularInline):
    model = ProductoImagen
    extra = 1
    # Esto asegura que aparezca la opción de borrar cada imagen de la galería
    can_delete = True 
    # Opcional: Mostrar una miniatura en la galería para saber qué borras
    readonly_fields = ('ver_miniatura',)

    def ver_miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.imagen.url)
        return "Sin imagen"
    ver_miniatura.short_description = "Miniatura"

class ProductoAdmin(admin.ModelAdmin):
    inlines = [ProductoImagenInline]
    list_display = ('title', 'user', 'price', 'created', 'ver_portada')
    
    # Añadimos la miniatura de la portada en el formulario de edición
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