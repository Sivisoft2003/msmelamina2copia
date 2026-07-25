from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product
from datetime import datetime
import random

class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('CREDITO', 'Crédito'),
        ('QR', 'QR / Transferencia'),
    ]
    
    STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('ANULADA', 'Anulada'),
        ('COTIZACION', 'Cotización/Proforma'),
    ]
    
    INVOICE_CHOICES = [
        ('SIN_IVA', 'Sin IVA (Consumidor Final)'),
        ('CON_IVA', 'Con Factura (16%)'),
    ]
    
    sale_number = models.CharField('Número de Venta', max_length=20, unique=True)
    date = models.DateTimeField('Fecha', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Vendedor')
    customer_name = models.CharField('Cliente', max_length=200, blank=True)
    customer_phone = models.CharField('Teléfono', max_length=20, blank=True)
    customer_nit = models.CharField('NIT/CI', max_length=20, blank=True)
    
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField('Descuento', max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField('IVA', max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField('Tasa IVA', max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    
    # Campos para pago y vuelto
    payment_method = models.CharField('Método de Pago', max_length=20, choices=PAYMENT_CHOICES, default='EFECTIVO')
    amount_paid = models.DecimalField('Monto Pagado', max_digits=12, decimal_places=2, default=0)
    change_amount = models.DecimalField('Vuelto', max_digits=12, decimal_places=2, default=0)
    
    # Tipo de documento
    is_quotation = models.BooleanField('¿Es Cotización/Proforma?', default=False)
    invoice_type = models.CharField('Tipo de Facturación', max_length=20, choices=INVOICE_CHOICES, default='SIN_IVA')
    invoice_number = models.CharField('Nº Factura', max_length=20, blank=True)
    
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='PENDIENTE')
    notes = models.TextField('Observaciones', blank=True)
    
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.sale_number} - {self.total} Bs."
    
    def save(self, *args, **kwargs):
        if not self.sale_number:
            prefix = 'COT' if self.is_quotation else 'VENTA'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_num = random.randint(100, 999)
            self.sale_number = f'{prefix}-{timestamp}-{random_num}'
        super().save(*args, **kwargs)

class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField('Cantidad', max_digits=12, decimal_places=2)
    unit_price = models.DecimalField('Precio Unitario', max_digits=12, decimal_places=2)
    discount = models.DecimalField('Descuento', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Ventas'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.total = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)
