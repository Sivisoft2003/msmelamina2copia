from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('api/search/', views.search_products, name='search_products'),
    path('api/process/', views.process_sale, name='process_sale'),
    path('api/barcode/', views.get_product_by_barcode, name='get_product_by_barcode'),
    path('recibo/<int:sale_id>/', views.generar_recibo, name='recibo'),
    path('', views.sale_list, name='list'),
    path('<int:pk>/', views.sale_detail, name='detail'),
    path('<int:pk>/anular/', views.sale_cancel, name='cancel'),
]
