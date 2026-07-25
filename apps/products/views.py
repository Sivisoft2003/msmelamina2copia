from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, ProductGroup, ProductCategory, Tag
from decimal import Decimal

@login_required
def product_list(request):
    """Lista de productos con búsqueda, filtros y tags"""
    products = Product.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(barcode__icontains=search) |
            Q(factory_code__icontains=search) |
            Q(tags__name__icontains=search)
        ).distinct()
    
    group_id = request.GET.get('group', '')
    if group_id:
        products = products.filter(group_id=group_id)
    
    tag_id = request.GET.get('tag', '')
    if tag_id:
        products = products.filter(tags__id=tag_id)
    
    all_tags = Tag.objects.filter(is_active=True)
    groups = ProductGroup.objects.all()
    
    context = {
        'products': products,
        'groups': groups,
        'tags': all_tags,
        'selected_tag': tag_id,
        'title': 'Productos'
    }
    return render(request, 'products/list.html', context)

@login_required
def product_create(request):
    """Crear producto"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            if not name:
                messages.error(request, 'El nombre del producto es obligatorio')
                raise Exception('Nombre requerido')
            
            product = Product.objects.create(
                code_level1=request.POST.get('code_level1', ''),
                code_level2=request.POST.get('code_level2', ''),
                code_level3=request.POST.get('code_level3', ''),
                code_level4=request.POST.get('code_level4', ''),
                barcode=request.POST.get('barcode', ''),
                factory_code=request.POST.get('factory_code', ''),
                name=name,
                description=request.POST.get('description', ''),
                unit=request.POST.get('unit', 'Unidad'),
                purchase_price=Decimal(request.POST.get('purchase_price', '0')) if request.POST.get('purchase_price') else Decimal('0'),
                sale_price=Decimal(request.POST.get('sale_price', '0')) if request.POST.get('sale_price') else Decimal('0'),
                current_stock=Decimal(request.POST.get('current_stock', '0')) if request.POST.get('current_stock') else Decimal('0'),
                min_stock=Decimal(request.POST.get('min_stock', '0')) if request.POST.get('min_stock') else Decimal('0'),
                max_stock=Decimal(request.POST.get('max_stock', '0')) if request.POST.get('max_stock') else Decimal('0'),
                is_active=request.POST.get('is_active') == 'on'
            )
            
            if request.POST.get('group'):
                product.group = ProductGroup.objects.get(id=request.POST.get('group'))
            if request.POST.get('category'):
                product.category = ProductCategory.objects.get(id=request.POST.get('category'))
            
            product.save()
            messages.success(request, f'✅ Producto "{product.name}" creado exitosamente')
            return redirect('products:detail', pk=product.pk)
            
        except Exception as e:
            messages.error(request, f'❌ Error al crear el producto: {str(e)}')
    
    groups = ProductGroup.objects.all()
    categories = ProductCategory.objects.all()
    return render(request, 'products/form.html', {
        'groups': groups,
        'categories': categories,
        'title': 'Crear Producto'
    })

@login_required
def product_detail(request, pk):
    """Detalle de producto"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {
        'product': product,
        'title': 'Detalle del Producto'
    })

@login_required
def product_edit(request, pk):
    """Editar producto"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.code_level1 = request.POST.get('code_level1', '')
            product.code_level2 = request.POST.get('code_level2', '')
            product.code_level3 = request.POST.get('code_level3', '')
            product.code_level4 = request.POST.get('code_level4', '')
            product.barcode = request.POST.get('barcode', '')
            product.factory_code = request.POST.get('factory_code', '')
            product.name = request.POST.get('name', '')
            product.description = request.POST.get('description', '')
            product.unit = request.POST.get('unit', 'Unidad')
            product.purchase_price = Decimal(request.POST.get('purchase_price', '0')) if request.POST.get('purchase_price') else Decimal('0')
            product.sale_price = Decimal(request.POST.get('sale_price', '0')) if request.POST.get('sale_price') else Decimal('0')
            product.current_stock = Decimal(request.POST.get('current_stock', '0')) if request.POST.get('current_stock') else Decimal('0')
            product.min_stock = Decimal(request.POST.get('min_stock', '0')) if request.POST.get('min_stock') else Decimal('0')
            product.max_stock = Decimal(request.POST.get('max_stock', '0')) if request.POST.get('max_stock') else Decimal('0')
            product.is_active = request.POST.get('is_active') == 'on'
            
            if request.POST.get('group'):
                product.group = ProductGroup.objects.get(id=request.POST.get('group'))
            if request.POST.get('category'):
                product.category = ProductCategory.objects.get(id=request.POST.get('category'))
            
            product.save()
            messages.success(request, f'✅ Producto "{product.name}" actualizado exitosamente')
            return redirect('products:detail', pk=product.pk)
            
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar el producto: {str(e)}')
    
    groups = ProductGroup.objects.all()
    categories = ProductCategory.objects.all()
    return render(request, 'products/form.html', {
        'product': product,
        'groups': groups,
        'categories': categories,
        'title': 'Editar Producto'
    })

@login_required
def product_delete(request, pk):
    """Eliminar producto (desactivar)"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, f'✅ Producto "{product.name}" desactivado exitosamente')
        return redirect('products:list')
    
    return render(request, 'products/delete.html', {
        'product': product,
        'title': 'Eliminar Producto'
    })
