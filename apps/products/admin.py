from django.contrib import admin
from .models import Product, ProductGroup, ProductCategory, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_color_display', 'is_auto', 'is_active']
    list_filter = ['color', 'is_auto', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']

@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'group']
    list_filter = ['group']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode', 'sale_price', 'current_stock', 'is_active']
    list_filter = ['group', 'category', 'is_active']  # 🔥 Quitar 'tags'
    search_fields = ['name', 'barcode', 'factory_code']
    list_editable = ['sale_price', 'current_stock']
    readonly_fields = ['full_code']
    
    # filter_horizontal = ['tags']  # 🔥 COMENTADO
    
    fieldsets = (
        ('Códigos', {
            'fields': ('code_level1', 'code_level2', 'code_level3', 'code_level4', 'barcode', 'factory_code')
        }),
        ('Información', {
            'fields': ('name', 'description', 'group', 'category', 'unit')
        }),
        ('Precios', {
            'fields': ('purchase_price', 'sale_price')
        }),
        ('Stock', {
            'fields': ('current_stock', 'min_stock', 'max_stock')
        }),
        # ('Etiquetas', {  # 🔥 COMENTADO
        #     'fields': ('tags',)
        # }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )