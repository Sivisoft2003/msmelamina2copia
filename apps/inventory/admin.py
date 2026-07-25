from django.contrib import admin
from .models import Warehouse, InventoryMovement, Stock

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'manager', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Información del Almacén', {
            'fields': ('name', 'code', 'address', 'manager')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ['date', 'warehouse', 'product', 'movement_type', 'quantity', 'unit_price', 'total']
    list_filter = ['movement_type', 'warehouse', 'date']
    search_fields = ['product__name', 'reference_number']
    readonly_fields = ['date', 'total']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('warehouse', 'product', 'movement_type')
        }),
        ('Cantidades', {
            'fields': ('quantity', 'unit_price', 'total')
        }),
        ('Referencia', {
            'fields': ('reference_type', 'reference_number')
        }),
        ('Observaciones', {
            'fields': ('notes', 'user')
        }),
    )

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['warehouse', 'product', 'quantity', 'last_update']
    list_filter = ['warehouse']
    search_fields = ['product__name']
    readonly_fields = ['last_update']
    
    fieldsets = (
        ('Información del Stock', {
            'fields': ('warehouse', 'product')
        }),
        ('Cantidad', {
            'fields': ('quantity',)
        }),
        ('Última Actualización', {
            'fields': ('last_update',)
        }),
    )
