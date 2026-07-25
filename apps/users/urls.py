from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Turnos
    path('', views.shift_dashboard, name='shift_dashboard'),
    path('turno/iniciar/', views.shift_start, name='shift_start'),
    path('turno/cerrar/', views.shift_close, name='shift_close'),
    path('turnos/', views.shift_history, name='shift_history'),
    
    # Usuarios (solo administradores)
    path('usuarios/', views.user_list, name='list'),
    path('usuarios/crear/', views.user_create, name='create'),
    path('usuarios/<int:pk>/editar/', views.user_edit, name='edit'),
    path('usuarios/<int:pk>/toggle/', views.user_toggle_active, name='toggle_active'),
]