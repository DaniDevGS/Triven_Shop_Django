from django.db import models
from django.contrib.auth.models import User


CATEGORIA_CHOICES = (
    ('SALUD', 'Salud y Belleza'),
    ('HIGIENE', 'Higiene'),
    ('COMESTIBLES', 'Comestibles'),
    ('OTROS', 'Otros'),
)



# Create your models here.
class Producto(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    cantidad = models.IntegerField(default=1) # Usaremos IntegerField para la cantidad
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    
    category = models.CharField(max_length=11, choices=CATEGORIA_CHOICES, default="OTROS")

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + '- by ' + self.user.username

