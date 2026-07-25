from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AuditLog
from .decorators import audit_log

@login_required
@staff_member_required
def audit_dashboard(request):
    """Dashboard de auditoría"""
    # Estadísticas
    total_acciones = AuditLog.objects.count()
    acciones_hoy = AuditLog.objects.filter(created_at__date=timezone.now().date()).count()
    
    # Acciones por módulo
    acciones_por_modulo = AuditLog.objects.values('module').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Acciones por usuario
    acciones_por_usuario = AuditLog.objects.values('user__username').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Últimas acciones
    ultimas_acciones = AuditLog.objects.select_related('user').order_by('-created_at')[:20]
    
    context = {
        'total_acciones': total_acciones,
        'acciones_hoy': acciones_hoy,
        'acciones_por_modulo': acciones_por_modulo,
        'acciones_por_usuario': acciones_por_usuario,
        'ultimas_acciones': ultimas_acciones,
        'title': 'Dashboard de Auditoría'
    }
    return render(request, 'audit/dashboard.html', context)

@login_required
@staff_member_required
def audit_list(request):
    """Lista de registros de auditoría con filtros"""
    logs = AuditLog.objects.select_related('user').all()
    
    # Filtros
    usuario = request.GET.get('usuario')
    accion = request.GET.get('accion')
    modulo = request.GET.get('modulo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if usuario:
        logs = logs.filter(user__username__icontains=usuario)
    if accion:
        logs = logs.filter(action=accion)
    if modulo:
        logs = logs.filter(module=modulo)
    if fecha_desde:
        logs = logs.filter(created_at__date__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(created_at__date__lte=fecha_hasta)
    
    # Obtener opciones para filtros
    usuarios = AuditLog.objects.values_list('user__username', flat=True).distinct()
    acciones = AuditLog.objects.values_list('action', flat=True).distinct()
    modulos = AuditLog.objects.values_list('module', flat=True).distinct()
    
    context = {
        'logs': logs,
        'usuarios': usuarios,
        'acciones': acciones,
        'modulos': modulos,
        'selected_usuario': usuario,
        'selected_accion': accion,
        'selected_modulo': modulo,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'title': 'Registros de Auditoría'
    }
    return render(request, 'audit/list.html', context)

@login_required
@staff_member_required
def audit_clean(request):
    """Limpiar logs antiguos"""
    if request.method == 'POST':
        dias = int(request.POST.get('dias', 90))
        fecha_limite = timezone.now() - timedelta(days=dias)
        count, _ = AuditLog.objects.filter(created_at__lt=fecha_limite).delete()
        
        messages.success(request, f'✅ {count} registros antiguos eliminados')
        return redirect('audit:list')
    
    context = {
        'title': 'Limpiar Logs'
    }
    return render(request, 'audit/clean.html', context)