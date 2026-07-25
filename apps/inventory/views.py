from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from decimal import Decimal
from .models import Warehouse, InventoryMovement, Stock
from apps.products.models import Product

@login_required
def inventory_list(request):
    """Lista de inventario con búsqueda y filtros"""
    warehouses = Warehouse.objects.filter(is_active=True)
    selected_warehouse = request.GET.get('warehouse')
    search = request.GET.get('search', '')
    
    if selected_warehouse:
        stocks = Stock.objects.filter(warehouse_id=selected_warehouse)
        warehouse = get_object_or_404(Warehouse, id=selected_warehouse)
    else:
        stocks = Stock.objects.all()
        warehouse = None
    
    if search:
        stocks = stocks.filter(
            Q(product__name__icontains=search) |
            Q(product__barcode__icontains=search) |
            Q(product__factory_code__icontains=search)
        )
    
    context = {
        'warehouses': warehouses,
        'stocks': stocks,
        'selected_warehouse': selected_warehouse,
        'warehouse': warehouse,
        'search': search,
        'title': 'Inventario'
    }
    return render(request, 'inventory/list.html', context)

@login_required
def inventory_movements(request):
    """Lista de movimientos de inventario"""
    movements = InventoryMovement.objects.select_related('product', 'warehouse', 'user').all()
    
    movement_type = request.GET.get('type')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    warehouse_id = request.GET.get('warehouse')
    if warehouse_id:
        movements = movements.filter(warehouse_id=warehouse_id)
    
    product_id = request.GET.get('product')
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    warehouses = Warehouse.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    context = {
        'movements': movements,
        'warehouses': warehouses,
        'products': products,
        'selected_type': movement_type,
        'selected_warehouse': warehouse_id,
        'selected_product': product_id,
        'title': 'Movimientos de Inventario'
    }
    return render(request, 'inventory/movements.html', context)

@login_required
@transaction.atomic
def inventory_entry(request):
    """Registrar entrada de inventario"""
    warehouses = Warehouse.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            warehouse_id = request.POST.get('warehouse')
            product_id = request.POST.get('product')
            quantity = request.POST.get('quantity')
            unit_price = request.POST.get('unit_price')
            notes = request.POST.get('notes', '')
            
            if not warehouse_id or not product_id or not quantity or not unit_price:
                messages.error(request, 'Todos los campos obligatorios deben ser completados')
                raise Exception('Campos obligatorios faltantes')
            
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)
            product = get_object_or_404(Product, id=product_id)
            
            # 🔥 CONVERTIR A DECIMAL
            quantity_decimal = Decimal(str(quantity))
            unit_price_decimal = Decimal(str(unit_price))
            
            # Crear movimiento
            InventoryMovement.objects.create(
                warehouse=warehouse,
                product=product,
                movement_type='ENTRADA',
                quantity=quantity_decimal,
                unit_price=unit_price_decimal,
                notes=notes,
                user=request.user
            )
            
            # Actualizar stock
            stock, created = Stock.objects.get_or_create(
                warehouse=warehouse,
                product=product,
                defaults={'quantity': Decimal('0')}
            )
            # 🔥 SUMAR CORRECTAMENTE
            stock.quantity = stock.quantity + quantity_decimal
            stock.save()
            
            # Actualizar stock del producto
            product.current_stock = product.current_stock + quantity_decimal
            product.save()
            
            messages.success(request, f'✅ Entrada registrada: {product.name} - {quantity} unidades')
            return redirect('inventory:movements')
            
        except Exception as e:
            messages.error(request, f'❌ Error al registrar entrada: {str(e)}')
    
    context = {
        'warehouses': warehouses,
        'products': products,
        'title': 'Registrar Entrada'
    }
    return render(request, 'inventory/entry.html', context)


@login_required
@transaction.atomic
def inventory_exit(request):
    """Registrar salida de inventario"""
    warehouses = Warehouse.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            warehouse_id = request.POST.get('warehouse')
            product_id = request.POST.get('product')
            quantity = request.POST.get('quantity')
            notes = request.POST.get('notes', '')
            
            if not warehouse_id or not product_id or not quantity:
                messages.error(request, 'Todos los campos obligatorios deben ser completados')
                raise Exception('Campos obligatorios faltantes')
            
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)
            product = get_object_or_404(Product, id=product_id)
            
            # 🔥 CONVERTIR A DECIMAL
            quantity_decimal = Decimal(str(quantity))
            
            # Verificar stock
            try:
                stock = Stock.objects.get(warehouse=warehouse, product=product)
            except Stock.DoesNotExist:
                messages.error(request, f'El producto no existe en el almacén {warehouse.name}')
                raise Exception('Producto no encontrado')
            
            # 🔥 COMPARAR DECIMAL CON DECIMAL
            if stock.quantity < quantity_decimal:
                messages.error(request, f'❌ Stock insuficiente. Disponible: {stock.quantity}')
                raise Exception('Stock insuficiente')
            
            # Crear movimiento
            InventoryMovement.objects.create(
                warehouse=warehouse,
                product=product,
                movement_type='SALIDA',
                quantity=quantity_decimal,
                unit_price=product.purchase_price or Decimal('0'),
                notes=notes,
                user=request.user
            )
            
            # 🔥 RESTAR CORRECTAMENTE
            stock.quantity = stock.quantity - quantity_decimal
            stock.save()
            
            # Actualizar stock del producto
            product.current_stock = product.current_stock - quantity_decimal
            product.save()
            
            messages.success(request, f'✅ Salida registrada: {product.name} - {quantity} unidades')
            return redirect('inventory:movements')
            
        except Exception as e:
            messages.error(request, f'❌ Error al registrar salida: {str(e)}')
    
    context = {
        'warehouses': warehouses,
        'products': products,
        'title': 'Registrar Salida'
    }
    return render(request, 'inventory/exit.html', context)

@login_required
def inventory_kardex(request, product_id):
    """Kardex de un producto"""
    product = get_object_or_404(Product, id=product_id)
    movements = InventoryMovement.objects.filter(product=product).select_related('warehouse').order_by('date')
    
    kardex_data = []
    balance = Decimal('0')
    for movement in movements:
        if movement.movement_type == 'ENTRADA':
            balance += movement.quantity
        else:
            balance -= movement.quantity
        
        kardex_data.append({
            'date': movement.date,
            'warehouse': movement.warehouse.name,
            'type': movement.movement_type,
            'quantity': float(movement.quantity),
            'unit_price': float(movement.unit_price),
            'total': float(movement.total),
            'balance': float(balance),
            'notes': movement.notes
        })
    
    context = {
        'product': product,
        'kardex_data': kardex_data,
        'title': f'Kardex - {product.name}'
    }
    return render(request, 'inventory/kardex.html', context)

# ============ NUEVAS FUNCIONALIDADES ============

@login_required
@transaction.atomic
def inventory_transfer(request):
    """Transferir productos entre almacenes"""
    warehouses = Warehouse.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            origen_id = request.POST.get('origen')
            destino_id = request.POST.get('destino')
            product_id = request.POST.get('product')
            quantity = request.POST.get('quantity')
            notes = request.POST.get('notes', '')
            
            if not origen_id or not destino_id or not product_id or not quantity:
                messages.error(request, 'Todos los campos son obligatorios')
                raise Exception('Campos obligatorios faltantes')
            
            origen = get_object_or_404(Warehouse, id=origen_id)
            destino = get_object_or_404(Warehouse, id=destino_id)
            product = get_object_or_404(Product, id=product_id)
            
            # 🔥 CONVERTIR A DECIMAL
            quantity_decimal = Decimal(str(quantity))
            
            # Verificar stock en origen
            try:
                stock_origen = Stock.objects.get(warehouse=origen, product=product)
            except Stock.DoesNotExist:
                messages.error(request, f'El producto no existe en el almacén {origen.name}')
                raise Exception('Producto no encontrado en origen')
            
            # 🔥 COMPARAR DECIMAL CON DECIMAL
            if stock_origen.quantity < quantity_decimal:
                messages.error(request, f'Stock insuficiente en {origen.name}. Disponible: {stock_origen.quantity}')
                raise Exception('Stock insuficiente')
            
            # Salida del origen
            InventoryMovement.objects.create(
                warehouse=origen,
                product=product,
                movement_type='TRANSFERENCIA',
                quantity=quantity_decimal,
                unit_price=product.purchase_price,
                notes=f"Transferencia a {destino.name}: {notes}",
                user=request.user
            )
            # 🔥 RESTAR CORRECTAMENTE (Decimal - Decimal)
            stock_origen.quantity = stock_origen.quantity - quantity_decimal
            stock_origen.save()
            
            # Entrada al destino
            InventoryMovement.objects.create(
                warehouse=destino,
                product=product,
                movement_type='ENTRADA',
                quantity=quantity_decimal,
                unit_price=product.purchase_price,
                notes=f"Transferencia desde {origen.name}: {notes}",
                user=request.user
            )
            stock_destino, created = Stock.objects.get_or_create(
                warehouse=destino,
                product=product,
                defaults={'quantity': Decimal('0')}
            )
            # 🔥 SUMAR CORRECTAMENTE (Decimal + Decimal)
            stock_destino.quantity = stock_destino.quantity + quantity_decimal
            stock_destino.save()
            
            # Actualizar stock del producto
            # 🔥 Mantener todo en Decimal
            product.current_stock = product.current_stock  # No cambia en transferencia
            product.save()
            
            messages.success(request, f'✅ Transferencia completada: {quantity} unidades de {product.name}')
            return redirect('inventory:movements')
            
        except Exception as e:
            messages.error(request, f'❌ Error en transferencia: {str(e)}')
    
    context = {
        'warehouses': warehouses,
        'products': products,
        'title': 'Transferencia entre Almacenes'
    }
    return render(request, 'inventory/transfer.html', context)

@login_required
@transaction.atomic
def inventory_adjust(request):
    """Ajustar inventario (correcciones)"""
    warehouses = Warehouse.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            warehouse_id = request.POST.get('warehouse')
            product_id = request.POST.get('product')
            new_quantity = request.POST.get('new_quantity')
            notes = request.POST.get('notes', '')
            
            warehouse = get_object_or_404(Warehouse, id=warehouse_id)
            product = get_object_or_404(Product, id=product_id)
            
            stock = Stock.objects.get(warehouse=warehouse, product=product)
            old_quantity = stock.quantity
            diferencia = float(new_quantity) - float(old_quantity)
            
            InventoryMovement.objects.create(
                warehouse=warehouse,
                product=product,
                movement_type='AJUSTE',
                quantity=abs(diferencia),
                unit_price=product.purchase_price,
                notes=f"Ajuste: {notes} (de {old_quantity} a {new_quantity})",
                user=request.user
            )
            
            stock.quantity = float(new_quantity)
            stock.save()
            
            product.current_stock += diferencia
            product.save()
            
            messages.success(request, f'✅ Ajuste realizado: {product.name} ahora tiene {new_quantity} unidades')
            return redirect('inventory:movements')
            
        except Exception as e:
            messages.error(request, f'❌ Error en ajuste: {str(e)}')
    
    context = {
        'warehouses': warehouses,
        'products': products,
        'title': 'Ajuste de Inventario'
    }
    return render(request, 'inventory/adjust.html', context)
