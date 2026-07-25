from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Sum, Q, F, Count  # 🔥 AGREGAR importación de models
from apps.products.models import Product
from apps.sales.models import Sale
from .models import Notification

class AlertGenerator:
    """Generador de alertas automáticas"""
    
    @staticmethod
    def check_stock_alerts():
        """Verificar stock bajo y sin stock"""
        from django.db import models  # 🔥 IMPORTAR AQUÍ TAMBIÉN
        
        # Stock Bajo
        productos_stock_bajo = Product.objects.filter(
            is_active=True,
            current_stock__gt=0,
            current_stock__lte=models.F('min_stock')
        )
        
        for product in productos_stock_bajo:
            # Buscar un usuario administrador para la notificación
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                Notification.objects.get_or_create(
                    user=admin_user,
                    title=f'⚠️ Stock Bajo: {product.name}',
                    notification_type='STOCK_BAJO',
                    defaults={
                        'message': f'El producto "{product.name}" tiene solo {product.current_stock} unidades en stock. Stock mínimo: {product.min_stock}',
                        'priority': 'ALTA',
                        'link': f'/products/{product.id}/'
                    }
                )
        
        # Sin Stock
        productos_sin_stock = Product.objects.filter(
            is_active=True,
            current_stock=0
        )
        
        for product in productos_sin_stock:
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                Notification.objects.get_or_create(
                    user=admin_user,
                    title=f'🚫 Sin Stock: {product.name}',
                    notification_type='SIN_STOCK',
                    defaults={
                        'message': f'El producto "{product.name}" está agotado. ¡Reabastece pronto!',
                        'priority': 'URGENTE',
                        'link': f'/products/{product.id}/'
                    }
                )
        
        return {
            'stock_bajo': productos_stock_bajo.count(),
            'sin_stock': productos_sin_stock.count()
        }
    
    @staticmethod
    def check_daily_sales():
        """Crear resumen de ventas del día"""
        hoy = timezone.now().date()
        usuarios = User.objects.filter(is_active=True)
        
        for user in usuarios:
            ventas_hoy = Sale.objects.filter(
                user=user,
                date__date=hoy,
                status='COMPLETADA'
            )
            
            total_ventas = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
            count_ventas = ventas_hoy.count()
            
            if total_ventas > 0:
                Notification.objects.get_or_create(
                    user=user,
                    title=f'📊 Ventas del Día',
                    notification_type='VENTA_DIA',
                    defaults={
                        'message': f'Has realizado {count_ventas} ventas por un total de Bs. {total_ventas:.2f}',
                        'priority': 'MEDIA',
                        'link': '/sales/'
                    }
                )
    
    @staticmethod
    def check_turno_activo():
        """Recordatorio de turno activo"""
        try:
            from apps.users.models import Shift
            
            turnos_activos = Shift.objects.filter(status='OPEN')
            
            for turno in turnos_activos:
                duracion = (timezone.now() - turno.start_time).total_seconds() / 3600
                if duracion > 6:
                    Notification.objects.get_or_create(
                        user=turno.user,
                        title='⏰ Recordatorio de Turno',
                        notification_type='TURNO',
                        defaults={
                            'message': f'Tu turno lleva {duracion:.1f} horas activo. ¿Deseas cerrarlo?',
                            'priority': 'MEDIA',
                            'link': '/users/'
                        }
                    )
        except:
            pass
    
    @staticmethod
    def generate_welcome_notification(user):
        """Generar notificación de bienvenida"""
        Notification.objects.get_or_create(
            user=user,
            title='👋 ¡Bienvenido a M&S Melamina!',
            notification_type='BIENVENIDA',
            defaults={
                'message': f'Bienvenido {user.username}. Hoy tienes {Product.objects.filter(is_active=True).count()} productos activos.',
                'priority': 'BAJA',
                'link': '/dashboard/'
            }
        )
