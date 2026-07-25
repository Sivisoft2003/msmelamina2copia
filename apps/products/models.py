from django.db import models
from django.core.validators import MinValueValidator

# ============ ETIQUETAS INTELIGENTES ============
class Tag(models.Model):
    """Modelo de etiqueta inteligente para productos"""
    COLOR_CHOICES = [
        ('primary', '🔵 Azul'),
        ('success', '🟢 Verde'),
        ('danger', '🔴 Rojo'),
        ('warning', '🟡 Amarillo'),
        ('info', '🔷 Celeste'),
        ('dark', '⚫ Negro'),
        ('purple', '🟣 Morado'),
        ('orange', '🟠 Naranja'),
    ]
    
    name = models.CharField('Nombre de la Etiqueta', max_length=50, unique=True)
    color = models.CharField('Color', max_length=20, choices=COLOR_CHOICES, default='primary')
    description = models.TextField('Descripción', blank=True)
    is_auto = models.BooleanField('¿Es automática?', default=False)
    is_active = models.BooleanField('Activa', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_color_class(self):
        return f'badge bg-{self.color}'

# ============ PRODUCTOS ============
class ProductGroup(models.Model):
    name = models.CharField('Nombre', max_length=100)
    code = models.CharField('Código', max_length=20, unique=True)
    description = models.TextField('Descripción', blank=True)
    
    class Meta:
        verbose_name = 'Grupo de Producto'
        verbose_name_plural = 'Grupos de Productos'
    
    def __str__(self):
        return self.name

class ProductCategory(models.Model):
    name = models.CharField('Nombre', max_length=100)
    group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name='categories')
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
    
    def __str__(self):
        return f"{self.group.name} - {self.name}"

class Product(models.Model):
    # Códigos
    code_level1 = models.CharField('Nivel 1', max_length=4, blank=True)
    code_level2 = models.CharField('Nivel 2', max_length=4, blank=True)
    code_level3 = models.CharField('Nivel 3', max_length=4, blank=True)
    code_level4 = models.CharField('Nivel 4', max_length=4, blank=True)
    
    # Códigos alternativos
    barcode = models.CharField('Código de Barras', max_length=50, unique=True, blank=True, null=True)
    factory_code = models.CharField('Código de Fábrica', max_length=50, blank=True)
    
    name = models.CharField('Nombre', max_length=200)
    description = models.TextField('Descripción', blank=True)
    
    # Clasificación
    group = models.ForeignKey(ProductGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    # Unidad
    unit = models.CharField('Unidad', max_length=20, default='Unidad')
    
    # Precios
    purchase_price = models.DecimalField('Precio de Compra', max_digits=12, decimal_places=2, default=0)
    sale_price = models.DecimalField('Precio de Venta', max_digits=12, decimal_places=2, default=0)
    
    # Stock
    current_stock = models.DecimalField('Stock Actual', max_digits=12, decimal_places=2, default=0)
    min_stock = models.DecimalField('Stock Mínimo', max_digits=12, decimal_places=2, default=0)
    max_stock = models.DecimalField('Stock Máximo', max_digits=12, decimal_places=2, default=0)
    
    # 🔥 ETIQUETAS - AGREGAR ESTA LÍNEA
    tags = models.ManyToManyField(Tag, blank=True, related_name='products', verbose_name='Etiquetas')
    
    # Estado
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def full_code(self):
        return f"{self.code_level1}{self.code_level2}{self.code_level3}{self.code_level4}"
