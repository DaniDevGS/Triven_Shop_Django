# forms.py

from django import forms
from .models import Producto, CATEGORIA_CHOICES

# 1. WIDGET: Heredamos de FileInput (no Clearable) para evitar conflictos de lógica
class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

# 2. CAMPO PERSONALIZADO: Esto le enseña a Django a validar una LISTA de archivos
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        # Si recibimos una lista (múltiples archivos), validamos cada uno
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProductForm(forms.ModelForm):
    # 3. USAMOS EL NUEVO CAMPO AQUÍ
    imagenes_extra = MultipleFileField(
        required=False,
        label="Imagenes de productos"
    )

    class Meta:
        model = Producto
        fields = ['imagen', 'imagenes_extra', 'title', 'description', 'price', 'cantidad', 'category']
        
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'id': 'input_imagen'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad', 'min': 1}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }