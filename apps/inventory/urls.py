from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='list'),
    path('movimientos/', views.inventory_movements, name='movements'),
    path('entrada/', views.inventory_entry, name='entry'),
    path('salida/', views.inventory_exit, name='exit'),
    path('transferencia/', views.inventory_transfer, name='transfer'),  # 🔥 NUEVA
    path('ajuste/', views.inventory_adjust, name='adjust'),  # 🔥 NUEVA
    path('kardex/<int:product_id>/', views.inventory_kardex, name='kardex'),
]