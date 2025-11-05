from django import forms
from .models import Producto, CATEGORIA_CHOICES

class ProductForm(forms.ModelForm):
    # Ya no definimos 'cantidad' aquí, sino en Meta.fields
    # El modelo ya tiene el campo, así que el ModelForm lo incluirá
    # por defecto si está en Meta.fields.
    class Meta:
        model = Producto
        # Incluye 'cantidad' en los campos del formulario
        fields = ['imagen','title', 'description', 'price', 'cantidad', 'category']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            # Puedes agregar un widget específico para 'cantidad' si lo deseas
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad', 'min': 1}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }