from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q, Sum
from django.contrib import messages
from django.utils import timezone
from apps.products.models import Product
from .models import Sale, SaleDetail
from .utils import generar_recibo_pdf
import json
from decimal import Decimal

# ============ PUNTO DE VENTA ============
@login_required
def pos_view(request):
    return render(request, 'sales/pos.html', {'title': 'Punto de Venta'})

@login_required
def search_products(request):
    query = request.GET.get('q', '')
    if query and len(query) >= 2:
        products = Product.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=query) |
            Q(barcode__icontains=query) |
            Q(factory_code__icontains=query)
        )[:20]
        
        data = []
        for product in products:
            data.append({
                'id': product.id,
                'name': product.name,
                'barcode': product.barcode or '',
                'sale_price': float(product.sale_price),
                'current_stock': float(product.current_stock),
                'unit': product.unit,
            })
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def process_sale(request):
    try:
        data = json.loads(request.body)
        
        is_quotation = data.get('is_quotation', False)
        invoice_type = data.get('invoice_type', 'SIN_IVA')
        
        # Verificar stock (solo si NO es cotización)
        if not is_quotation:
            for item in data.get('items', []):
                product = Product.objects.get(id=item['id'])
                if product.current_stock < item['quantity']:
                    return JsonResponse({
                        'success': False,
                        'error': f'Stock insuficiente para {product.name}. Disponible: {product.current_stock}'
                    }, status=400)
        
        # Calcular IVA
        subtotal = Decimal(str(data.get('subtotal', 0)))
        tax_rate = Decimal('0.16') if invoice_type == 'CON_IVA' else Decimal('0')
        tax = subtotal * tax_rate
        total = subtotal - Decimal(str(data.get('discount', 0))) + tax
        
        # Crear la venta
        sale = Sale.objects.create(
            user=request.user,
            customer_name=data.get('customer_name', ''),
            customer_phone=data.get('customer_phone', ''),
            customer_nit=data.get('customer_nit', ''),
            subtotal=subtotal,
            discount=Decimal(str(data.get('discount', 0))),
            tax=tax,
            tax_rate=tax_rate,
            total=total,
            payment_method=data.get('payment_method', 'EFECTIVO'),
            amount_paid=Decimal(str(data.get('amount_paid', 0))),
            change_amount=Decimal(str(data.get('change_amount', 0))),
            is_quotation=is_quotation,
            invoice_type=invoice_type,
            status='COTIZACION' if is_quotation else 'COMPLETADA',
            notes=data.get('notes', '')
        )
        
        # Crear detalles
        for item in data.get('items', []):
            product = get_object_or_404(Product, id=item['id'])
            
            SaleDetail.objects.create(
                sale=sale,
                product=product,
                quantity=Decimal(str(item['quantity'])),
                unit_price=Decimal(str(item['price'])),
                total=Decimal(str(item['total']))
            )
            
            # Actualizar stock (solo si NO es cotización)
            if not is_quotation:
                product.current_stock -= Decimal(str(item['quantity']))
                product.save()
        
        return JsonResponse({
            'success': True,
            'sale_id': sale.id,
            'sale_number': sale.sale_number,
            'total': float(total),
            'is_quotation': is_quotation
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def get_product_by_barcode(request):
    barcode = request.GET.get('barcode', '')
    if barcode:
        try:
            product = Product.objects.get(barcode=barcode, is_active=True)
            data = {
                'id': product.id,
                'name': product.name,
                'barcode': product.barcode,
                'sale_price': float(product.sale_price),
                'current_stock': float(product.current_stock),
                'unit': product.unit,
            }
            return JsonResponse(data)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    return JsonResponse({'error': 'Código de barras requerido'}, status=400)

@login_required
def generar_recibo(request, sale_id):
    """Generar y descargar recibo PDF"""
    # 🔥 PERMITIR ADMINISTRADORES VER TODOS LOS RECIBOS
    if request.user.is_superuser:
        sale = get_object_or_404(Sale, id=sale_id)
    else:
        sale = get_object_or_404(Sale, id=sale_id, user=request.user)
    
    try:
        pdf = generar_recibo_pdf(sale)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        tipo = 'COTIZACION' if sale.is_quotation else 'RECIBO'
        response['Content-Disposition'] = f'attachment; filename="{tipo}_{sale.sale_number}.pdf"'
        return response
    except Exception as e:
        return JsonResponse({'error': f'Error al generar PDF: {str(e)}'}, status=500)

# ============ HISTORIAL DE VENTAS ============
@login_required
def sale_list(request):
    """Lista de todas las ventas incluyendo cotizaciones"""
    # 🔥 Mostrar TODAS las ventas (COMPLETADAS, PENDIENTES, COTIZACIONES)
    sales = Sale.objects.all().order_by('-date')
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    cliente = request.GET.get('cliente')
    tipo = request.GET.get('tipo')  # Nuevo filtro por tipo
    
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            sales = sales.filter(date__date__gte=fecha_desde_obj)
        except:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
            sales = sales.filter(date__date__lte=fecha_hasta_obj)
        except:
            pass
    
    if cliente:
        sales = sales.filter(customer_name__icontains=cliente)
    
    if tipo:
        if tipo == 'COMPLETADA':
            sales = sales.filter(status='COMPLETADA')
        elif tipo == 'COTIZACION':
            sales = sales.filter(status='COTIZACION')
        elif tipo == 'PENDIENTE':
            sales = sales.filter(status='PENDIENTE')
        elif tipo == 'ANULADA':
            sales = sales.filter(status='ANULADA')
    
    # Estadísticas
    total_ventas = sales.count()
    total_monto = sales.aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'sales': sales,
        'total_ventas': total_ventas,
        'total_monto': total_monto,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'cliente': cliente,
        'tipo': tipo,
        'title': 'Historial de Ventas'
    }
    return render(request, 'sales/list.html', context)

@login_required
def sale_detail(request, pk):
    """Detalle de una venta"""
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/detail.html', {'sale': sale, 'title': 'Detalle de Venta'})

@login_required
def sale_cancel(request, pk):
    """Anular una venta (solo si es COMPLETADA)"""
    sale = get_object_or_404(Sale, pk=pk)
    
    if sale.status == 'ANULADA':
        messages.warning(request, 'Esta venta ya fue anulada')
        return redirect('sales:detail', pk=pk)
    
    if sale.status == 'COTIZACION':
        messages.warning(request, 'Las cotizaciones no se pueden anular')
        return redirect('sales:detail', pk=pk)
    
    if sale.status == 'PENDIENTE':
        messages.warning(request, 'Las ventas pendientes no se pueden anular')
        return redirect('sales:detail', pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo', 'Sin motivo')
        sale.status = 'ANULADA'
        sale.notes = f"ANULADA: {motivo} - {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        sale.save()
        
        # Devolver stock (solo si era COMPLETADA)
        if sale.status == 'COMPLETADA':
            for detail in sale.details.all():
                detail.product.current_stock += detail.quantity
                detail.product.save()
        
        messages.success(request, f'✅ Venta {sale.sale_number} anulada exitosamente')
        return redirect('sales:list')
    
    return render(request, 'sales/cancel.html', {'sale': sale, 'title': 'Anular Venta'})