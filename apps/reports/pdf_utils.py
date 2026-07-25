from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime
import os

def get_company_settings():
    """Obtener configuración de la empresa"""
    try:
        from apps.core.models import CompanySettings
        return CompanySettings.get_settings()
    except:
        return None
def generar_pdf_reporte(data, headers, title, filename, total=None):
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.png')
    if os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=3*cm, height=1.5*cm)
            elements.append(logo)
            elements.append(Spacer(1, 0.3*cm))
        except Exception as e:
            print(f"Error al cargar logo: {e}")
    """
    Genera un PDF con formato de reporte usando ReportLab
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=5
    )
    style_subtitle = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=5
    )
    style_company = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=5
    )
    style_header = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.white,
        backColor=colors.HexColor('#2C3E50')
    )
    style_cell = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=8
    )
    style_cell_right = ParagraphStyle(
        'CellRight',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_RIGHT
    )
    
    company = get_company_settings()
    company_name = company.company_name if company else 'M&S Melamina'
    
    # Elementos del PDF
    elements = []
    
    # ============ LOGO ============
    if company and company.logo:
        logo_path = os.path.join(settings.MEDIA_ROOT, str(company.logo))
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=4*cm, height=2*cm)
                elements.append(logo)
                elements.append(Spacer(1, 0.2*cm))
            except Exception as e:
                print(f"Error al cargar logo: {e}")
    
    # ============ ENCABEZADO ============
    elements.append(Paragraph(company_name, style_company))
    if company and company.nit:
        elements.append(Paragraph(f'NIT: {company.nit}', style_subtitle))
    if company and company.address:
        elements.append(Paragraph(company.address, style_subtitle))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(title, style_title))
    elements.append(Paragraph(f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M")}', style_subtitle))
    elements.append(Spacer(1, 0.5*cm))
    
    # ============ TABLA DE DATOS ============
    if data:
        # Preparar datos para la tabla
        table_data = []
        
        # Encabezados
        header_row = []
        for h in headers:
            header_row.append(Paragraph(f'<b>{h}</b>', style_header))
        table_data.append(header_row)
        
        # Datos
        for row in data:
            row_data = []
            for value in row:
                if isinstance(value, (int, float)):
                    row_data.append(Paragraph(f'Bs. {value:,.2f}', style_cell_right))
                else:
                    row_data.append(Paragraph(str(value), style_cell))
            table_data.append(row_data)
        
        # Totales
        if total is not None:
            total_row = [''] * len(headers)
            total_row[0] = Paragraph('<b>TOTAL</b>', style_cell)
            total_row[-1] = Paragraph(f'<b>Bs. {total:,.2f}</b>', style_cell_right)
            table_data.append(total_row)
        
        # Crear tabla
        col_widths = [doc.width / len(headers)] * len(headers)
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
    
    # ============ PIE DE PÁGINA ============
    elements.append(Spacer(1, 1*cm))
    if company and company.receipt_footer:
        elements.append(Paragraph(company.receipt_footer, style_subtitle))
    elements.append(Paragraph('Este documento es un comprobante generado por el sistema', style_subtitle))
    
    # Construir PDF
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


def generar_reporte_ventas_pdf(sales, total_ventas, total_monto, fecha_desde=None, fecha_hasta=None):
    """Generar reporte de ventas en PDF"""
    headers = ['N° Venta', 'Fecha', 'Cliente', 'Vendedor', 'Total']
    
    data = []
    for sale in sales[:50]:  # Limitar a 50 registros
        data.append([
            sale.sale_number,
            sale.date.strftime('%d/%m/%Y %H:%M'),
            sale.customer_name or 'Consumidor Final',
            sale.user.username,
            float(sale.total)
        ])
    
    title = 'REPORTE DE VENTAS'
    if fecha_desde or fecha_hasta:
        title += f' ({fecha_desde or ""} - {fecha_hasta or ""})'
    
    return generar_pdf_reporte(data, headers, title, 'reporte_ventas', total=float(total_monto))


def generar_reporte_productos_pdf(products, total_productos):
    """Generar reporte de productos en PDF"""
    headers = ['Producto', 'Código', 'Categoría', 'Precio Venta', 'Stock']
    
    data = []
    for product in products[:50]:  # Limitar a 50 registros
        data.append([
            product.name,
            product.barcode or '-',
            product.category.name if product.category else 'Sin categoría',
            float(product.sale_price),
            float(product.current_stock)
        ])
    
    return generar_pdf_reporte(data, headers, 'REPORTE DE PRODUCTOS', 'reporte_productos')


def generar_reporte_inventario_pdf(stocks, total_valorizado):
    """Generar reporte de inventario en PDF"""
    headers = ['Almacén', 'Producto', 'Código', 'Cantidad', 'Valor']
    
    data = []
    for stock in stocks[:50]:  # Limitar a 50 registros
        valor = float(stock.quantity) * float(stock.product.purchase_price)
        data.append([
            stock.warehouse.name,
            stock.product.name,
            stock.product.barcode or '-',
            float(stock.quantity),
            valor
        ])
    
    return generar_pdf_reporte(data, headers, 'REPORTE DE INVENTARIO VALORADO', 'reporte_inventario', total=float(total_valorizado))


def generar_kardex_pdf(product, movements):
    """Generar kardex de producto en PDF"""
    headers = ['Fecha', 'Almacén', 'Tipo', 'Entrada', 'Salida', 'Saldo']
    
    data = []
    balance = 0
    for movement in movements:
        if movement.movement_type == 'ENTRADA':
            balance += float(movement.quantity)
            data.append([
                movement.date.strftime('%d/%m/%Y %H:%M'),
                movement.warehouse.name,
                'Entrada',
                float(movement.quantity),
                '',
                balance
            ])
        else:
            balance -= float(movement.quantity)
            data.append([
                movement.date.strftime('%d/%m/%Y %H:%M'),
                movement.warehouse.name,
                'Salida',
                '',
                float(movement.quantity),
                balance
            ])
    
    title = f'KARDEX - {product.name}'
    return generar_pdf_reporte(data, headers, title, f'kardex_{product.name}')
