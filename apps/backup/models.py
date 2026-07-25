from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Backup(models.Model):
    """Modelo de respaldo de base de datos"""
    
    STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('FALLIDO', 'Fallido'),
        ('RESTAURADO', 'Restaurado'),
    ]
    
    name = models.CharField('Nombre del Respaldo', max_length=100)
    file_path = models.CharField('Ruta del Archivo', max_length=500)
    file_size = models.BigIntegerField('Tamaño (bytes)', default=0)
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='PENDIENTE')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Creado por')
    notes = models.TextField('Observaciones', blank=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    restored_at = models.DateTimeField('Restaurado', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Respaldo'
        verbose_name_plural = 'Respaldos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def get_file_size_display(self):
        """Retorna el tamaño en formato legible"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.2f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.2f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.2f} GB"