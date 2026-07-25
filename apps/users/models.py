from django.db import models
from django.contrib.auth.models import User

class Shift(models.Model):
    """Modelo de Turno de Trabajo"""
    SHIFT_TYPES = [
        ('MORNING', 'Turno Mañana'),
        ('AFTERNOON', 'Turno Tarde'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Abierto'),
        ('CLOSED', 'Cerrado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuario')
    shift_type = models.CharField('Tipo de Turno', max_length=20, choices=SHIFT_TYPES)
    start_time = models.DateTimeField('Hora de Inicio', auto_now_add=True)
    end_time = models.DateTimeField('Hora de Cierre', null=True, blank=True)
    initial_cash = models.DecimalField('Efectivo Inicial', max_digits=12, decimal_places=2, default=0)
    final_cash = models.DecimalField('Efectivo Final', max_digits=12, decimal_places=2, null=True, blank=True)
    sales_count = models.IntegerField('Número de Ventas', default=0)
    total_sales = models.DecimalField('Total Ventas', max_digits=12, decimal_places=2, default=0)
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='OPEN')
    notes = models.TextField('Observaciones', blank=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_shift_type_display()} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"
    
    def duration(self):
        """Duración del turno en horas"""
        if self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600
        return None