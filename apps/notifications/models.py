from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    """Modelo de notificaciones del sistema"""
    
    TYPES = [
        ('STOCK_BAJO', '⚠️ Stock Bajo'),
        ('SIN_STOCK', '🚫 Sin Stock'),
        ('VENTA_DIA', '📊 Ventas del Día'),
        ('TURNO', '⏰ Recordatorio de Turno'),
        ('BIENVENIDA', '👋 Bienvenida'),
        ('ALERTA', '🔔 Alerta General'),
        ('SISTEMA', '⚙️ Sistema'),
    ]
    
    PRIORITY_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones', verbose_name='Usuario')
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensaje')
    notification_type = models.CharField('Tipo', max_length=20, choices=TYPES)
    priority = models.CharField('Prioridad', max_length=20, choices=PRIORITY_CHOICES, default='MEDIA')
    is_read = models.BooleanField('Leída', default=False)
    link = models.CharField('Enlace', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    @classmethod
    def create_stock_alert(cls, product):
        """Crear alerta de stock bajo"""
        user = product.user if hasattr(product, 'user') else User.objects.filter(is_superuser=True).first()
        if user:
            return cls.objects.create(
                user=user,
                title=f'⚠️ Stock Bajo: {product.name}',
                message=f'El producto "{product.name}" tiene solo {product.current_stock} unidades en stock. Stock mínimo: {product.min_stock}',
                notification_type='STOCK_BAJO',
                priority='ALTA',
                link=f'/products/{product.id}/'
            )
        return None