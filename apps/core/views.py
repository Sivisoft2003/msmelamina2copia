from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from apps.products.models import Product
from apps.sales.models import Sale
from apps.inventory.models import InventoryMovement
from apps.core.models import CompanySettings

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:login')

@login_required
def home(request):
    return redirect('core:dashboard')

@login_required
def dashboard(request):
    """Dashboard con estadísticas en tiempo real"""
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    
    # Estadísticas de productos
    total_productos = Product.objects.filter(is_active=True).count()
    productos_stock_bajo = Product.objects.filter(
        is_active=True, 
        current_stock__lte=F('min_stock')
    ).count()
    
    # Ventas de los últimos 7 días
    ventas_dias = []
    labels_dias = []
    
    for i in range(6, -1, -1):
        fecha = hoy - timedelta(days=i)
        ventas_dia = Sale.objects.filter(
            date__date=fecha,
            status='COMPLETADA'
        )
        total_dia = ventas_dia.aggregate(total=Sum('total'))['total'] or 0
        ventas_dias.append(float(total_dia))
        labels_dias.append(fecha.strftime('%d/%m'))
    
    # Ventas hoy
    try:
        ventas_hoy = Sale.objects.filter(
            date__date=hoy,
            status='COMPLETADA'
        )
        total_ventas_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
        total_ventas_hoy_count = ventas_hoy.count()
    except:
        total_ventas_hoy = 0
        total_ventas_hoy_count = 0
    
    # Ventas del mes
    try:
        ventas_mes = Sale.objects.filter(
            date__date__gte=inicio_mes,
            date__date__lte=hoy,
            status='COMPLETADA'
        )
        total_ventas_mes = ventas_mes.aggregate(total=Sum('total'))['total'] or 0
        total_ventas_mes_count = ventas_mes.count()
    except:
        total_ventas_mes = 0
        total_ventas_mes_count = 0
    
    # Top productos
    try:
        from apps.sales.models import SaleDetail
        top_productos = SaleDetail.objects.filter(
            sale__status='COMPLETADA'
        ).values('product__name').annotate(
            total_vendido=Sum('quantity')
        ).order_by('-total_vendido')[:5]
    except:
        top_productos = []
    
    # Últimas ventas
    try:
        ultimas_ventas = Sale.objects.filter(
            status='COMPLETADA'
        ).order_by('-date')[:5]
    except:
        ultimas_ventas = []
    
    # Movimientos de inventario
    try:
        movimientos_hoy = InventoryMovement.objects.filter(date__date=hoy).count()
    except:
        movimientos_hoy = 0
    
    # Configuración de la empresa
    try:
        company = CompanySettings.get_settings()
    except:
        company = None
    
    context = {
        'total_productos': total_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'total_ventas_hoy': total_ventas_hoy,
        'total_ventas_hoy_count': total_ventas_hoy_count,
        'total_ventas_mes': total_ventas_mes,
        'total_ventas_mes_count': total_ventas_mes_count,
        'ventas_dias': ventas_dias,
        'labels_dias': labels_dias,
        'top_productos': top_productos,
        'ultimas_ventas': ultimas_ventas,
        'movimientos_hoy': movimientos_hoy,
        'fecha_actual': hoy,
        'company': company,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def settings_view(request):
    """Vista para configurar la empresa"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para acceder a esta página')
        return redirect('core:dashboard')
    
    from .forms import CompanySettingsForm
    
    settings = CompanySettings.get_settings()
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Configuración actualizada exitosamente')
            return redirect('core:settings')
        else:
            messages.error(request, '❌ Error al actualizar la configuración')
    else:
        form = CompanySettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
        'title': 'Configuración de la Empresa'
    }
    return render(request, 'core/settings.html', context)
