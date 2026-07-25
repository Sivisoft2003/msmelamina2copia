from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_action_display', 'get_module_display', 'description', 'created_at']
    list_filter = ['action', 'module', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['user', 'action', 'module', 'description', 'details', 'ip_address', 'user_agent', 'created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser