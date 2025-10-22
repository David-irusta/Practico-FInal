from django.db import models
from django.conf import settings
from django.utils import timezone
from productos.models import Producto
from cliente.models import Cliente

class Venta(models.Model):
    codigo = models.CharField("Codigo de venta", max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    fecha = models.DateTimeField("Fecha de venta", default=timezone.now)
    total = models.DecimalField("Total", max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.codigo} - {self.fecha.date()} - {self.total}"
    
class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField("Cantidad")
    precio_unitario = models.DecimalField("Precio unitario", max_digits=10, decimal_places=2)
    subtotal = models.DecimalField("Subtotal", max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} x {self.precio_unitario}"
