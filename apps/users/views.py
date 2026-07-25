from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from .models import Shift
from .forms import UserCreateForm
from apps.sales.models import Sale

# 🔥 DECORADOR PARA ADMINISTRADORES
def admin_required(view_func):
    """Decorador para permitir solo a superusuarios"""
    return user_passes_test(lambda u: u.is_superuser)(view_func)


# ============ TURNOS (TODOS LOS USUARIOS) ============
@login_required
def shift_dashboard(request):
    """Dashboard de turnos"""
    turno_actual = Shift.objects.filter(user=request.user, status='OPEN').first()
    historial_turnos = Shift.objects.filter(user=request.user).order_by('-start_time')[:10]
    
    context = {
        'turno_actual': turno_actual,
        'historial_turnos': historial_turnos,
        'title': 'Mis Turnos'
    }
    return render(request, 'users/shift_dashboard.html', context)

@login_required
def shift_start(request):
    """Iniciar turno"""
    turno_actual = Shift.objects.filter(user=request.user, status='OPEN').first()
    if turno_actual:
        messages.warning(request, 'Ya tienes un turno abierto')
        return redirect('users:shift_dashboard')
    
    if request.method == 'POST':
        shift_type = request.POST.get('shift_type')
        initial_cash = request.POST.get('initial_cash', 0)
        notes = request.POST.get('notes', '')
        
        shift = Shift.objects.create(
            user=request.user,
            shift_type=shift_type,
            initial_cash=initial_cash,
            notes=notes,
            status='OPEN'
        )
        
        messages.success(request, f'✅ Turno {shift.get_shift_type_display()} iniciado')
        return redirect('users:shift_dashboard')
    
    return render(request, 'users/shift_start.html', {'title': 'Iniciar Turno'})

@login_required
@transaction.atomic
def shift_close(request):
    """Cerrar turno"""
    turno = Shift.objects.filter(user=request.user, status='OPEN').first()
    if not turno:
        messages.error(request, 'No tienes un turno abierto')
        return redirect('users:shift_dashboard')
    
    if request.method == 'POST':
        final_cash = request.POST.get('final_cash')
        notes = request.POST.get('notes', '')
        
        ventas = Sale.objects.filter(
            user=request.user,
            date__gte=turno.start_time,
            status='COMPLETADA'
        )
        
        turno.sales_count = ventas.count()
        turno.total_sales = ventas.aggregate(total=Sum('total'))['total'] or 0
        turno.final_cash = final_cash
        turno.status = 'CLOSED'
        turno.end_time = timezone.now()
        turno.notes = notes
        turno.save()
        
        messages.success(request, f'✅ Turno cerrado. Ventas: {turno.sales_count}, Total: Bs. {turno.total_sales}')
        return redirect('users:shift_dashboard')
    
    ventas = Sale.objects.filter(
        user=request.user,
        date__gte=turno.start_time,
        status='COMPLETADA'
    )
    
    total_ventas = ventas.aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'turno': turno,
        'ventas_count': ventas.count(),
        'total_ventas': total_ventas,
        'title': 'Cerrar Turno'
    }
    return render(request, 'users/shift_close.html', context)

@login_required
def shift_history(request):
    """Historial de turnos"""
    turnos = Shift.objects.filter(user=request.user).order_by('-start_time')
    
    context = {
        'turnos': turnos,
        'title': 'Historial de Turnos'
    }
    return render(request, 'users/shift_history.html', context)


# ============ USUARIOS (SOLO ADMINISTRADORES) ============
@login_required
@admin_required
def user_list(request):
    """Lista de usuarios (solo administradores)"""
    users = User.objects.all()
    context = {
        'users': users,
        'title': 'Usuarios'
    }
    return render(request, 'users/user_list.html', context)

@login_required
@admin_required
def user_create(request):
    """Crear nuevo usuario (solo administradores)"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'✅ Usuario "{user.username}" creado exitosamente')
            return redirect('users:list')
    else:
        form = UserCreateForm()
    
    return render(request, 'users/user_form.html', {
        'form': form,
        'title': 'Crear Usuario'
    })

@login_required
@admin_required
def user_edit(request, pk):
    """Editar usuario (solo administradores)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Usuario "{user.username}" actualizado exitosamente')
            return redirect('users:list')
    else:
        form = UserCreateForm(instance=user)
    
    return render(request, 'users/user_form.html', {
        'form': form,
        'user': user,
        'title': 'Editar Usuario'
    })

@login_required
@admin_required
def user_toggle_active(request, pk):
    """Activar/Desactivar usuario (solo administradores)"""
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    
    estado = "activado" if user.is_active else "desactivado"
    messages.success(request, f'✅ Usuario "{user.username}" {estado}')
    return redirect('users:list')