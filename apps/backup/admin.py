from django.contrib import admin
from .models import Backup

@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_file_size_display', 'status', 'created_by', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'notes']
    readonly_fields = ['created_at', 'file_size']
    list_editable = ['status']