from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification
from .alert_generator import AlertGenerator

@login_required
def notification_list(request):
    """Lista de notificaciones del usuario"""
    notificaciones = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    
    # Marcar todas como leídas si se solicita
    if request.GET.get('mark_all_read'):
        notificaciones.update(is_read=True)
        messages.success(request, '✅ Todas las notificaciones marcadas como leídas')
        return redirect('notifications:list')
    
    context = {
        'notificaciones': notificaciones,
        'total': notificaciones.count(),
        'no_leidas': notificaciones.filter(is_read=False).count(),
        'title': 'Notificaciones'
    }
    return render(request, 'notifications/list.html', context)

@login_required
def notification_read(request, pk):
    """Marcar notificación como leída"""
    notificacion = get_object_or_404(Notification, pk=pk, user=request.user)
    notificacion.is_read = True
    notificacion.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:list')

@login_required
def notification_delete(request, pk):
    """Eliminar notificación"""
    notificacion = get_object_or_404(Notification, pk=pk, user=request.user)
    notificacion.delete()
    messages.success(request, '✅ Notificación eliminada')
    return redirect('notifications:list')

@login_required
def generate_alerts(request):
    """Generar alertas manualmente (solo superusuario)"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción')
        return redirect('core:dashboard')
    
    AlertGenerator.check_stock_alerts()
    AlertGenerator.check_daily_sales()
    AlertGenerator.check_turno_activo()
    
    messages.success(request, '✅ Alertas generadas correctamente')
    return redirect('notifications:list')

@login_required
def clear_all_notifications(request):
    """Eliminar todas las notificaciones (solo superusuario)"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para esta acción')
        return redirect('core:dashboard')
    
    count = Notification.objects.filter(user=request.user).delete()
    messages.success(request, f'✅ {count[0]} notificaciones eliminadas')
    return redirect('notifications:list')