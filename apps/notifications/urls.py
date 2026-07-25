from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('leer/<int:pk>/', views.notification_read, name='read'),
    path('eliminar/<int:pk>/', views.notification_delete, name='delete'),
    path('generar/', views.generate_alerts, name='generate'),
    path('limpiar/', views.clear_all_notifications, name='clear_all'),
]