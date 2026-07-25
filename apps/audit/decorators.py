from functools import wraps
from .models import AuditLog

def audit_log(action, module, description_func=None):
    """
    Decorador para registrar acciones automáticamente
    
    Args:
        action: Tipo de acción (CREATE, UPDATE, DELETE, etc.)
        module: Módulo donde se ejecuta la acción
        description_func: Función que retorna la descripción (recibe request y *args)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Ejecutar la vista
            response = view_func(request, *args, **kwargs)
            
            # Solo registrar si el usuario está autenticado
            if request.user.is_authenticated:
                # Obtener descripción
                if description_func:
                    description = description_func(request, *args, **kwargs)
                else:
                    description = f"Acción {action} en {module}"
                
                # Registrar
                AuditLog.log_action(
                    user=request.user,
                    action=action,
                    module=module,
                    description=description,
                    request=request
                )
            
            return response
        return wrapper
    return decorator


def audit_login(view_func):
    """Decorador para registrar login"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        if request.user.is_authenticated:
            AuditLog.log_action(
                user=request.user,
                action='LOGIN',
                module='AUDIT',
                description=f'Inicio de sesión desde IP: {request.META.get("REMOTE_ADDR")}',
                request=request
            )
        
        return response
    return wrapper


def audit_logout(view_func):
    """Decorador para registrar logout"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        response = view_func(request, *args, **kwargs)
        
        if user.is_authenticated:
            AuditLog.log_action(
                user=user,
                action='LOGOUT',
                module='AUDIT',
                description=f'Cierre de sesión',
                request=request
            )
        
        return response
    return wrapper