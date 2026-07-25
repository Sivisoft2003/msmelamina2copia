from django import forms
from .models import CompanySettings

class CompanySettingsForm(forms.ModelForm):
    """Formulario para la configuración de la empresa"""
    
    class Meta:
        model = CompanySettings
        fields = [
            'company_name', 'nit', 'address', 'phone', 'email', 'website', 'logo',
            'currency', 'currency_symbol', 'iva_rate',
            'receipt_footer', 'receipt_message',
            'print_auto', 'copies',
            'low_stock_alert',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'nit': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'currency_symbol': forms.TextInput(attrs={'class': 'form-control'}),
            'iva_rate': forms.Select(attrs={'class': 'form-select'}),
            'receipt_footer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'receipt_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'print_auto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'low_stock_alert': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
