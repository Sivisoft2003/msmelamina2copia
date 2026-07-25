from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('ventas/', views.sales_report, name='sales'),
    path('productos/', views.products_report, name='products'),
    path('inventario/', views.inventory_report, name='inventory'),
    path('vendedores/', views.vendedores_report, name='vendedores'),  # 🔥 NUEVO
    
    # Exportar a Excel
    path('exportar/ventas/', views.export_sales, name='export_sales'),
    path('exportar/productos/', views.export_products, name='export_products'),
    path('exportar/inventario/', views.export_inventory, name='export_inventory'),
    
    # Exportar a PDF
    path('exportar/ventas/pdf/', views.export_sales_pdf, name='export_sales_pdf'),
    path('exportar/productos/pdf/', views.export_products_pdf, name='export_products_pdf'),
    path('exportar/inventario/pdf/', views.export_inventory_pdf, name='export_inventory_pdf'),
    path('exportar/kardex/<int:product_id>/pdf/', views.export_kardex_pdf, name='export_kardex_pdf'),
]