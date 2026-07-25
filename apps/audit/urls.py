from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_dashboard, name='dashboard'),
    path('logs/', views.audit_list, name='list'),
    path('limpiar/', views.audit_clean, name='clean'),
]