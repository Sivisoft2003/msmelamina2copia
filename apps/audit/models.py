from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AuditLog(models.Model):
    """Modelo de registro de auditoría"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('VIEW', 'Ver'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('EXPORT', 'Exportar'),
        ('PRINT', 'Imprimir'),
        ('CANCEL', 'Anular'),
        ('RESTORE', 'Restaurar'),
    ]
    
    MODULE_CHOICES = [
        ('PRODUCTS', 'Productos'),
        ('SALES', 'Ventas'),
        ('INVENTORY', 'Inventario'),
        ('USERS', 'Usuarios'),
        ('REPORTS', 'Reportes'),
        ('BACKUP', 'Respaldos'),
        ('SETTINGS', 'Configuración'),
        ('TURNS', 'Turnos'),
        ('AUDIT', 'Auditoría'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Usuario')
    action = models.CharField('Acción', max_length=20, choices=ACTION_CHOICES)
    module = models.CharField('Módulo', max_length=20, choices=MODULE_CHOICES)
    description = models.TextField('Descripción')
    details = models.JSONField('Detalles', default=dict, blank=True)
    ip_address = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.TextField('Navegador', blank=True)
    created_at = models.DateTimeField('Fecha', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'module']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def log_action(cls, user, action, module, description, details=None, request=None):
        """Método para registrar una acción"""
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(
            user=user,
            action=action,
            module=module,
            description=description,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )