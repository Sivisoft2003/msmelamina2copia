from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.backup_list, name='list'),
    path('crear/', views.backup_create, name='create'),
    path('descargar/<int:pk>/', views.backup_download, name='download'),
    path('restaurar/<int:pk>/', views.backup_restore, name='restore'),
    path('eliminar/<int:pk>/', views.backup_delete, name='delete'),
    path('limpiar/', views.backup_clean, name='clean'),
]