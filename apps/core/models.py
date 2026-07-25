from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CompanySettings(models.Model):
    """Configuración de la empresa"""
    
    # Datos de la empresa
    company_name = models.CharField('Nombre de la Empresa', max_length=200, default='M&S Melamina')
    nit = models.CharField('NIT', max_length=20, default='123456789')
    address = models.TextField('Dirección', blank=True, default='Santa Cruz - Bolivia')
    phone = models.CharField('Teléfono', max_length=20, blank=True, default='+(591) 3-1234567')
    email = models.EmailField('Email', blank=True, default='info@msmelamina.com')
    website = models.URLField('Sitio Web', blank=True)
    
    # Logo
    logo = models.ImageField('Logo', upload_to='logos/', blank=True, null=True)
    
    # Configuración financiera
    currency = models.CharField('Moneda', max_length=10, default='Bs.')
    currency_symbol = models.CharField('Símbolo de Moneda', max_length=5, default='Bs.')
    
    IVA_CHOICES = [
        (0, '0% (Exento)'),
        (13, '13% (Bolivia)'),
        (16, '16% (Con Factura)'),
    ]
    iva_rate = models.IntegerField('Tasa de IVA (%)', choices=IVA_CHOICES, default=13)
    
    # Configuración de recibos
    receipt_footer = models.TextField('Pie de página del recibo', blank=True, default='¡Gracias por su compra!')
    receipt_message = models.TextField('Mensaje en el recibo', blank=True, default='Este documento es un comprobante de venta')
    
    # Configuración de impresión
    print_auto = models.BooleanField('Imprimir recibo automáticamente', default=False)
    copies = models.IntegerField('Número de copias', default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Configuración de inventario
    low_stock_alert = models.IntegerField('Alerta de stock bajo (unidades)', default=10)
    
    # Fechas
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración de la Empresa'
        verbose_name_plural = 'Configuraciones de la Empresa'
    
    def __str__(self):
        return self.company_name
    
    def save(self, *args, **kwargs):
        # Solo permitir una configuración activa
        if not self.pk and CompanySettings.objects.exists():
            raise ValueError('Ya existe una configuración. Edita la existente.')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Obtiene la configuración activa o crea una por defecto"""
        settings, created = cls.objects.get_or_create(
            id=1,
            defaults={
                'company_name': 'M&S Melamina',
                'nit': '123456789',
                'address': 'Santa Cruz - Bolivia',
                'phone': '+(591) 3-1234567',
                'email': 'info@msmelamina.com',
                'currency': 'Bs.',
                'currency_symbol': 'Bs.',
                'iva_rate': 13,
                'receipt_footer': '¡Gracias por su compra!',
                'receipt_message': 'Este documento es un comprobante de venta',
                'low_stock_alert': 10,
                'print_auto': False,
                'copies': 1,
            }
        )
        return settings