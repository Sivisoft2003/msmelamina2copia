from django.contrib import admin
from .models import CompanySettings

@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'nit', 'phone', 'iva_rate', 'currency']
    fieldsets = (
        ('Datos de la Empresa', {
            'fields': ('company_name', 'nit', 'address', 'phone', 'email', 'website', 'logo')
        }),
        ('Configuración Financiera', {
            'fields': ('currency', 'currency_symbol', 'iva_rate')
        }),
        ('Configuración de Recibos', {
            'fields': ('receipt_footer', 'receipt_message')
        }),
        ('Configuración de Impresión', {
            'fields': ('print_auto', 'copies')
        }),
        ('Configuración de Inventario', {
            'fields': ('low_stock_alert',)
        }),
    )