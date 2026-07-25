from .models import Product, Tag
from django.db.models import F, Sum, Q
from django.utils import timezone
from datetime import timedelta

def generar_tags_automaticos():
    """Genera etiquetas automáticas para productos"""
    
    # 1. Etiqueta: Stock Bajo
    tag_stock_bajo, _ = Tag.objects.get_or_create(
        name='Stock Bajo',
        defaults={
            'color': 'danger',
            'description': 'Productos con stock crítico',
            'is_auto': True
        }
    )
    
    # 2. Etiqueta: Más Vendido
    tag_mas_vendido, _ = Tag.objects.get_or_create(
        name='Más Vendido',
        defaults={
            'color': 'success',
            'description': 'Productos más vendidos del mes',
            'is_auto': True
        }
    )
    
    # 3. Etiqueta: Nuevo
    tag_nuevo, _ = Tag.objects.get_or_create(
        name='Nuevo',
        defaults={
            'color': 'info',
            'description': 'Productos nuevos (menos de 7 días)',
            'is_auto': True
        }
    )
    
    # 4. Etiqueta: Sin Stock
    tag_sin_stock, _ = Tag.objects.get_or_create(
        name='Sin Stock',
        defaults={
            'color': 'dark',
            'description': 'Productos agotados',
            'is_auto': True
        }
    )
    
    # 5. Etiqueta: En Oferta
    tag_oferta, _ = Tag.objects.get_or_create(
        name='En Oferta',
        defaults={
            'color': 'warning',
            'description': 'Productos en oferta',
            'is_auto': False  # Manual
        }
    )
    
    return {
        'stock_bajo': tag_stock_bajo,
        'mas_vendido': tag_mas_vendido,
        'nuevo': tag_nuevo,
        'sin_stock': tag_sin_stock,
        'oferta': tag_oferta,
    }

def actualizar_tags_productos():
    """Actualiza las etiquetas automáticas de todos los productos"""
    from apps.sales.models import SaleDetail
    
    # Obtener tags automáticos
    tags = generar_tags_automaticos()
    
    # 🔥 OBTENER TODOS LOS PRODUCTOS ACTIVOS
    productos = Product.objects.filter(is_active=True)
    
    # 1. Limpiar tags automáticos de todos los productos
    for product in productos:
        # 🔥 CORRECCIÓN: Usar remove() en lugar de update()
        product.tags.remove(tags['stock_bajo'])
        product.tags.remove(tags['sin_stock'])
        product.tags.remove(tags['nuevo'])
    
    # 2. Asignar tags según condiciones
    for product in productos:
        # Stock Bajo: current_stock <= min_stock y > 0
        if product.current_stock <= product.min_stock and product.current_stock > 0:
            product.tags.add(tags['stock_bajo'])
        
        # Sin Stock: current_stock == 0
        if product.current_stock == 0:
            product.tags.add(tags['sin_stock'])
        
        # Nuevo: creado en los últimos 7 días
        if timezone.now() - product.created_at <= timedelta(days=7):
            product.tags.add(tags['nuevo'])
    
    # 3. Más Vendido (Top 5 del mes)
    # 🔥 CORRECCIÓN: Usar clear() y add() en lugar de update()
    inicio_mes = timezone.now().date().replace(day=1)
    
    # Limpiar tag 'Más Vendido' de todos los productos
    for product in Product.objects.all():
        product.tags.remove(tags['mas_vendido'])
    
    # Obtener top 5 productos del mes
    top_productos = SaleDetail.objects.filter(
        sale__date__date__gte=inicio_mes,
        sale__status='COMPLETADA'
    ).values('product_id').annotate(
        total_vendido=Sum('quantity')
    ).order_by('-total_vendido')[:5]
    
    # Asignar tag a los top 5
    for item in top_productos:
        try:
            product = Product.objects.get(id=item['product_id'])
            product.tags.add(tags['mas_vendido'])
        except Product.DoesNotExist:
            pass
    
    print(f'✅ Tags automáticos actualizados')
    print(f'   - Stock Bajo: {Product.objects.filter(tags=tags["stock_bajo"]).count()} productos')
    print(f'   - Sin Stock: {Product.objects.filter(tags=tags["sin_stock"]).count()} productos')
    print(f'   - Nuevo: {Product.objects.filter(tags=tags["nuevo"]).count()} productos')
    print(f'   - Más Vendido: {Product.objects.filter(tags=tags["mas_vendido"]).count()} productos')