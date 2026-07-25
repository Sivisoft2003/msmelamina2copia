from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from apps.sales.models import Sale, SaleDetail
from apps.products.models import Product
from apps.inventory.models import Stock
from .utils import export_sales_report, export_products_report, export_inventory_report
from .pdf_utils import (
    generar_reporte_ventas_pdf,
    generar_reporte_productos_pdf,
    generar_reporte_inventario_pdf,
    generar_kardex_pdf
)
import json

# ============ EXPORTAR A PDF ============

@login_required
def export_sales_pdf(request):
    """Exportar ventas a PDF"""
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    sales = Sale.objects.filter(status='COMPLETADA').order_by('-date')
    
    if fecha_desde:
        sales = sales.filter(date__date__gte=fecha_desde)
    if fecha_hasta:
        sales = sales.filter(date__date__lte=fecha_hasta)
    
    total_ventas = sales.count()
    total_monto = sales.aggregate(total=Sum('total'))['total'] or 0
    
    return generar_reporte_ventas_pdf(sales, total_ventas, total_monto, fecha_desde, fecha_hasta)

@login_required
def export_products_pdf(request):
    """Exportar productos a PDF"""
    products = Product.objects.filter(is_active=True).order_by('name')
    total_productos = products.count()
    return generar_reporte_productos_pdf(products, total_productos)

@login_required
def export_inventory_pdf(request):
    """Exportar inventario a PDF"""
    stocks = Stock.objects.select_related('product', 'warehouse').all()
    total_valorizado = 0
    for stock in stocks:
        total_valorizado += float(stock.quantity) * float(stock.product.purchase_price)
    return generar_reporte_inventario_pdf(stocks, total_valorizado)

@login_required
def export_kardex_pdf(request, product_id):
    """Exportar kardex de producto a PDF"""
    from apps.inventory.models import InventoryMovement
    product = get_object_or_404(Product, id=product_id)
    movements = InventoryMovement.objects.filter(product=product).order_by('date')
    return generar_kardex_pdf(product, movements)

@login_required
def reports_dashboard(request):
    return render(request, 'reports/dashboard.html', {'title': 'Reportes'})

@login_required
def sales_report(request):
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)
    
    # 🔥 SOLO COMPLETADAS
    estado_valido = 'COMPLETADA'
    
    # Ventas de hoy
    ventas_hoy = Sale.objects.filter(date__date=hoy, status=estado_valido)
    total_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    count_hoy = ventas_hoy.count()
    
    # Ventas de la semana
    ventas_semana = Sale.objects.filter(
        date__date__gte=inicio_semana,
        date__date__lte=hoy,
        status=estado_valido
    )
    total_semana = ventas_semana.aggregate(total=Sum('total'))['total'] or 0
    count_semana = ventas_semana.count()
    
    # Ventas del mes
    ventas_mes = Sale.objects.filter(
        date__date__gte=inicio_mes,
        date__date__lte=hoy,
        status=estado_valido
    )
    total_mes = ventas_mes.aggregate(total=Sum('total'))['total'] or 0
    count_mes = ventas_mes.count()
    
    # Ventas por día (últimos 7 días)
    ventas_dias = []
    for i in range(6, -1, -1):
        fecha = hoy - timedelta(days=i)
        ventas_dia = Sale.objects.filter(date__date=fecha, status=estado_valido)
        total_dia = ventas_dia.aggregate(total=Sum('total'))['total'] or 0
        ventas_dias.append({
            'fecha': fecha.strftime('%d/%m'),
            'total': float(total_dia),
            'count': ventas_dia.count()
        })
    
    # Ventas para exportar
    ventas_export = Sale.objects.filter(
        date__date__gte=inicio_mes,
        date__date__lte=hoy,
        status=estado_valido
    ).order_by('-date')
    
    context = {
        'total_hoy': total_hoy,
        'count_hoy': count_hoy,
        'total_semana': total_semana,
        'count_semana': count_semana,
        'total_mes': total_mes,
        'count_mes': count_mes,
        'ventas_dias': json.dumps(ventas_dias),
        'ventas_export': ventas_export,
        'title': 'Reporte de Ventas'
    }
    return render(request, 'reports/sales_report.html', context)

@login_required
def products_report(request):
    # 🔥 SOLO COMPLETADAS
    estado_valido = 'COMPLETADA'
    
    top_productos = SaleDetail.objects.filter(
        sale__status=estado_valido
    ).values(
        'product__id',
        'product__name',
        'product__sale_price'
    ).annotate(
        total_vendido=Sum('quantity'),
        total_ingresos=Sum('total')
    ).order_by('-total_vendido')[:10]
    
    productos_stock_bajo = Product.objects.filter(
        is_active=True,
        current_stock__lte=10
    )[:10]
    
    todos_productos = Product.objects.filter(is_active=True).order_by('name')
    
    context = {
        'top_productos': top_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'todos_productos': todos_productos,
        'title': 'Reporte de Productos'
    }
    return render(request, 'reports/products_report.html', context)

@login_required
def inventory_report(request):
    stocks = Stock.objects.select_related('product', 'warehouse').all()
    
    total_valorizado = 0
    productos_stock = []
    
    for stock in stocks:
        valor = float(stock.quantity) * float(stock.product.purchase_price)
        total_valorizado += valor
        productos_stock.append({
            'producto': stock.product.name,
            'codigo': stock.product.barcode or '-',
            'warehouse': stock.warehouse.name,
            'cantidad': float(stock.quantity),
            'precio_compra': float(stock.product.purchase_price),
            'valor': valor
        })
    
    resumen_almacen = Stock.objects.values('warehouse__name').annotate(
        total_productos=Count('product'),
        total_cantidad=Sum('quantity')
    )
    
    context = {
        'productos_stock': productos_stock[:50],
        'total_valorizado': total_valorizado,
        'resumen_almacen': resumen_almacen,
        'title': 'Reporte de Inventario'
    }
    return render(request, 'reports/inventory_report.html', context)

# ============ EXPORTAR A EXCEL ============

@login_required
def export_sales(request):
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    sales = Sale.objects.filter(status='COMPLETADA').order_by('-date')
    
    if fecha_desde:
        sales = sales.filter(date__date__gte=fecha_desde)
    if fecha_hasta:
        sales = sales.filter(date__date__lte=fecha_hasta)
    
    return export_sales_report(sales)

@login_required
def export_products(request):
    products = Product.objects.filter(is_active=True).order_by('name')
    return export_products_report(products)

@login_required
def export_inventory(request):
    stocks = Stock.objects.select_related('product', 'warehouse').all()
    return export_inventory_report(stocks)
@login_required
def vendedores_report(request):
    """Reporte de rendimiento de vendedores"""
    
    # Solo administradores pueden ver este reporte
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para ver este reporte')
        return redirect('reports:dashboard')
    
    # Obtener parámetros de filtro
    periodo = request.GET.get('periodo', 'semana')  # dia, semana, mes, personalizado
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    vendedor_id = request.GET.get('vendedor')
    
    # Calcular fechas según período
    hoy = timezone.now().date()
    
    if periodo == 'dia':
        fecha_inicio = hoy
        fecha_fin = hoy
        titulo_periodo = 'Hoy'
    elif periodo == 'semana':
        fecha_inicio = hoy - timedelta(days=hoy.weekday())
        fecha_fin = hoy
        titulo_periodo = 'Esta Semana'
    elif periodo == 'mes':
        fecha_inicio = hoy.replace(day=1)
        fecha_fin = hoy
        titulo_periodo = 'Este Mes'
    elif periodo == 'personalizado' and fecha_desde and fecha_hasta:
        fecha_inicio = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        titulo_periodo = f'{fecha_desde} al {fecha_hasta}'
    else:
        fecha_inicio = hoy - timedelta(days=30)
        fecha_fin = hoy
        titulo_periodo = 'Últimos 30 días'
    
    # Obtener todos los usuarios (vendedores)
    if vendedor_id:
        vendedores = User.objects.filter(id=vendedor_id, is_active=True)
    else:
        vendedores = User.objects.filter(is_active=True)
    
    # Datos de cada vendedor
    datos_vendedores = []
    
    for vendedor in vendedores:
        # Ventas del vendedor en el período
        ventas = Sale.objects.filter(
            user=vendedor,
            date__date__gte=fecha_inicio,
            date__date__lte=fecha_fin,
            status='COMPLETADA'
        )
        
        total_ventas = ventas.count()
        total_monto = ventas.aggregate(total=Sum('total'))['total'] or 0
        promedio = total_monto / total_ventas if total_ventas > 0 else 0
        
        # Obtener productos más vendidos por este vendedor
        top_productos = SaleDetail.objects.filter(
            sale__in=ventas
        ).values('product__name').annotate(
            cantidad=Sum('quantity')
        ).order_by('-cantidad')[:3]
        
        datos_vendedores.append({
            'id': vendedor.id,
            'username': vendedor.username,
            'full_name': vendedor.get_full_name() or vendedor.username,
            'total_ventas': total_ventas,
            'total_monto': total_monto,
            'promedio': promedio,
            'top_productos': list(top_productos),
            'is_superuser': vendedor.is_superuser,
        })
    
    # Ordenar por monto total (mayor a menor)
    datos_vendedores.sort(key=lambda x: x['total_monto'], reverse=True)
    
    # Estadísticas generales
    total_general = sum(v['total_monto'] for v in datos_vendedores)
    total_ventas_general = sum(v['total_ventas'] for v in datos_vendedores)
    
    # Lista de vendedores para el filtro
    lista_vendedores = User.objects.filter(is_active=True)
    
    context = {
        'datos_vendedores': datos_vendedores,
        'total_general': total_general,
        'total_ventas_general': total_ventas_general,
        'titulo_periodo': titulo_periodo,
        'periodo': periodo,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'lista_vendedores': lista_vendedores,
        'vendedor_seleccionado': vendedor_id,
        'title': 'Reporte de Vendedores'
    }
    return render(request, 'reports/vendedores_report.html', context)