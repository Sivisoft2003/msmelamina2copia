import os
import shutil
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from .models import Backup

def crear_respaldo(usuario, notas=''):
    """
    Crea un respaldo de la base de datos
    
    Args:
        usuario: Usuario que realiza el respaldo
        notas: Observaciones del respaldo
    
    Returns:
        Backup: Objeto del respaldo creado
    """
    # Crear carpeta de backups si no existe
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Nombre del archivo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup_{timestamp}.sqlite3'
    filepath = os.path.join(backup_dir, filename)
    
    # Crear respaldo
    db_path = settings.DATABASES['default']['NAME']
    
    try:
        shutil.copy2(db_path, filepath)
        
        # Registrar en la base de datos
        backup = Backup.objects.create(
            name=f'Respaldo {timestamp}',
            file_path=filepath,
            file_size=os.path.getsize(filepath),
            status='COMPLETADO',
            created_by=usuario,
            notes=notas
        )
        
        return backup
    except Exception as e:
        # Registrar error
        backup = Backup.objects.create(
            name=f'Respaldo {timestamp}',
            file_path='',
            file_size=0,
            status='FALLIDO',
            created_by=usuario,
            notes=f'Error: {str(e)}'
        )
        return backup


def restaurar_respaldo(backup_id, usuario):
    """
    Restaura un respaldo de la base de datos
    
    Args:
        backup_id: ID del respaldo a restaurar
        usuario: Usuario que realiza la restauración
    
    Returns:
        bool: True si se restauró correctamente
    """
    try:
        backup = Backup.objects.get(id=backup_id)
        
        if not os.path.exists(backup.file_path):
            raise Exception('El archivo de respaldo no existe')
        
        # Hacer backup del archivo actual
        db_path = settings.DATABASES['default']['NAME']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_actual = f'{db_path}.pre_restore_{timestamp}'
        shutil.copy2(db_path, backup_actual)
        
        # Restaurar
        shutil.copy2(backup.file_path, db_path)
        
        # Actualizar estado
        backup.status = 'RESTAURADO'
        backup.restored_at = datetime.now()
        backup.save()
        
        return True
    except Exception as e:
        raise Exception(f'Error al restaurar: {str(e)}')


def eliminar_respaldo(backup_id):
    """
    Elimina un respaldo (archivo y registro)
    
    Args:
        backup_id: ID del respaldo a eliminar
    
    Returns:
        bool: True si se eliminó correctamente
    """
    try:
        backup = Backup.objects.get(id=backup_id)
        
        # Eliminar archivo
        if os.path.exists(backup.file_path):
            os.remove(backup.file_path)
        
        # Eliminar registro
        backup.delete()
        
        return True
    except Exception as e:
        raise Exception(f'Error al eliminar: {str(e)}')


def limpiar_respaldos_antiguos(dias=30):
    """
    Elimina respaldos más antiguos que los días especificados
    
    Args:
        dias: Número de días para conservar
    """
    from django.utils import timezone
    from datetime import timedelta
    
    fecha_limite = timezone.now() - timedelta(days=dias)
    respaldos_antiguos = Backup.objects.filter(
        created_at__lt=fecha_limite
    )
    
    for backup in respaldos_antiguos:
        try:
            if os.path.exists(backup.file_path):
                os.remove(backup.file_path)
            backup.delete()
        except:
            pass
    
    return respaldos_antiguos.count()