from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
from decimal import Decimal

class Warehouse(models.Model):
    """Modelo de Almacén"""
    name = models.CharField('Nombre', max_length=100)
    code = models.CharField('Código', max_length=20, unique=True)
    address = models.TextField('Dirección', blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Encargado')
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Almacén'
        verbose_name_plural = 'Almacenes'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class InventoryMovement(models.Model):
    """Modelo de Movimiento de Inventario"""
    MOVEMENT_TYPES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('AJUSTE', 'Ajuste'),
        ('BAJA', 'Baja'),
    ]
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='Almacén')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Producto')
    movement_type = models.CharField('Tipo de Movimiento', max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField('Cantidad', max_digits=12, decimal_places=2)
    unit_price = models.DecimalField('Precio Unitario', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    
    reference_type = models.CharField('Tipo de Referencia', max_length=20, blank=True)
    reference_number = models.CharField('Número de Referencia', max_length=50, blank=True)
    
    notes = models.TextField('Observaciones', blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuario')
    date = models.DateTimeField('Fecha', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.movement_type} - {self.product.name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        quantity = Decimal(str(self.quantity)) if self.quantity else Decimal('0')
        unit_price = Decimal(str(self.unit_price)) if self.unit_price else Decimal('0')
        self.total = quantity * unit_price
        super().save(*args, **kwargs)

class Stock(models.Model):
    """Modelo de Stock por Almacén"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='Almacén')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Producto')
    quantity = models.DecimalField('Cantidad', max_digits=12, decimal_places=2, default=0)
    last_update = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        unique_together = ['warehouse', 'product']
        ordering = ['product__name']
    
    def __str__(self):
        return f"{self.warehouse.name} - {self.product.name}: {self.quantity}"
