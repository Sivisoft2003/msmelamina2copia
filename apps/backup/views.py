from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import Backup
from .backup_utils import crear_respaldo, restaurar_respaldo, eliminar_respaldo, limpiar_respaldos_antiguos
import os

@login_required
@staff_member_required
def backup_list(request):
    """Lista de respaldos"""
    respaldos = Backup.objects.all().order_by('-created_at')
    
    context = {
        'respaldos': respaldos,
        'title': 'Respaldos'
    }
    return render(request, 'backup/list.html', context)

@login_required
@staff_member_required
def backup_create(request):
    """Crear respaldo manual"""
    if request.method == 'POST':
        notas = request.POST.get('notas', '')
        backup = crear_respaldo(request.user, notas)
        
        if backup.status == 'COMPLETADO':
            messages.success(request, f'✅ Respaldo creado exitosamente: {backup.name}')
        else:
            messages.error(request, f'❌ Error al crear respaldo: {backup.notes}')
        
        return redirect('backup:list')
    
    context = {
        'title': 'Crear Respaldo'
    }
    return render(request, 'backup/create.html', context)

@login_required
@staff_member_required
def backup_download(request, pk):
    """Descargar archivo de respaldo"""
    backup = get_object_or_404(Backup, pk=pk)
    
    if not os.path.exists(backup.file_path):
        messages.error(request, 'El archivo de respaldo no existe')
        return redirect('backup:list')
    
    response = FileResponse(open(backup.file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(backup.file_path)}"'
    return response

@login_required
@staff_member_required
def backup_restore(request, pk):
    """Restaurar respaldo"""
    backup = get_object_or_404(Backup, pk=pk)
    
    if request.method == 'POST':
        try:
            restaurar_respaldo(pk, request.user)
            messages.success(request, f'✅ Respaldo restaurado exitosamente: {backup.name}')
            return redirect('backup:list')
        except Exception as e:
            messages.error(request, f'❌ Error al restaurar: {str(e)}')
    
    context = {
        'backup': backup,
        'title': 'Restaurar Respaldo'
    }
    return render(request, 'backup/restore.html', context)

@login_required
@staff_member_required
def backup_delete(request, pk):
    """Eliminar respaldo"""
    backup = get_object_or_404(Backup, pk=pk)
    
    if request.method == 'POST':
        try:
            eliminar_respaldo(pk)
            messages.success(request, f'✅ Respaldo eliminado: {backup.name}')
            return redirect('backup:list')
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar: {str(e)}')
    
    context = {
        'backup': backup,
        'title': 'Eliminar Respaldo'
    }
    return render(request, 'backup/delete.html', context)

@login_required
@staff_member_required
def backup_clean(request):
    """Limpiar respaldos antiguos"""
    if request.method == 'POST':
        dias = int(request.POST.get('dias', 30))
        count = limpiar_respaldos_antiguos(dias)
        messages.success(request, f'✅ {count} respaldos antiguos eliminados')
        return redirect('backup:list')
    
    context = {
        'title': 'Limpiar Respaldos'
    }
    return render(request, 'backup/clean.html', context)