from .models import Notification

def notifications_processor(request):
    """Procesador de contexto para notificaciones"""
    if request.user.is_authenticated:
        notificaciones = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).order_by('-created_at')[:10]
        
        total_no_leidas = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return {
            'notificaciones': notificaciones,
            'total_notificaciones': total_no_leidas
        }
    return {
        'notificaciones': [],
        'total_notificaciones': 0
    }