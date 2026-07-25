from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os

def generar_recibo_pdf(sale):
    # ... código existente ...
    
    # ============ LOGO RECTANGULAR ============
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.png')
    if os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, 2*cm, height - 3.5*cm, width=3*cm, height=2*cm, mask='auto')
        except:
            pass
    
    # ... resto del código ...
    """Genera un recibo/cotización en PDF"""
    buffer = BytesIO()
    
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Logo
    try:
        logo_path = os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.png')
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            c.drawImage(logo, 2*cm, height - 3.5*cm, width=3*cm, height=2.5*cm, mask='auto')
    except:
        pass
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(5.5*cm, height - 2.2*cm, "M & S TOOLS")
    c.setFont("Helvetica", 8)
    c.drawString(5.5*cm, height - 2.7*cm, "Innovación en Herramientas y Accesorios")
    c.setFont("Helvetica", 9)
    c.drawString(5.5*cm, height - 3.2*cm, "Cochabamba - Bolivia")
    c.drawString(5.5*cm, height - 3.7*cm, "NIT: 3480401018")
    
    # Línea
    y = height - 4.5*cm
    c.line(2*cm, y, width - 2*cm, y)
    
    # Tipo de documento
    y = y - 1*cm
    c.setFont("Helvetica-Bold", 14)
    titulo = "COTIZACIÓN / PROFORMA" if sale.is_quotation else "RECIBO DE VENTA"
    c.drawString(2*cm, y, titulo)
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y - 0.6*cm, f"Número: {sale.sale_number}")
    c.drawString(2*cm, y - 1.2*cm, f"Fecha: {sale.date.strftime('%d/%m/%Y %H:%M')}")
    c.drawString(2*cm, y - 1.8*cm, f"Vendedor: {sale.user.get_full_name() or sale.user.username}")
    
    # Cliente
    y = y - 3*cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, y, "DATOS DEL CLIENTE")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y - 0.6*cm, f"Nombre: {sale.customer_name or 'Consumidor Final'}")
    c.drawString(2*cm, y - 1.2*cm, f"NIT/CI: {sale.customer_nit or 'No registrado'}")
    c.drawString(2*cm, y - 1.8*cm, f"Teléfono: {sale.customer_phone or 'No registrado'}")
    
    # Línea
    y = y - 2.5*cm
    c.line(2*cm, y, width - 2*cm, y)
    
    # Productos
    y = y - 0.8*cm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, y, "Cant.")
    c.drawString(4*cm, y, "Producto")
    c.drawString(12*cm, y, "Precio")
    c.drawString(15*cm, y, "Total")
    
    y = y - 0.3*cm
    c.line(2*cm, y, width - 2*cm, y)
    
    c.setFont("Helvetica", 9)
    y = y - 0.6*cm
    for detail in sale.details.all():
        c.drawString(2*cm, y, str(detail.quantity))
        c.drawString(4*cm, y, detail.product.name[:40])
        c.drawString(12*cm, y, f"Bs. {detail.unit_price:.2f}")
        c.drawString(15*cm, y, f"Bs. {detail.total:.2f}")
        y = y - 0.5*cm
    
    # Totales
    y = y - 0.3*cm
    c.line(2*cm, y, width - 2*cm, y)
    
    y = y - 0.8*cm
    c.setFont("Helvetica", 10)
    c.drawString(10*cm, y, "Subtotal:")
    c.drawString(15*cm, y, f"Bs. {sale.subtotal:.2f}")
    y = y - 0.5*cm
    
    if sale.tax_rate > 0:
        c.drawString(10*cm, y, f"IVA ({int(sale.tax_rate*100)}%):")
        c.drawString(15*cm, y, f"Bs. {sale.tax:.2f}")
        y = y - 0.5*cm
    
    if sale.discount > 0:
        c.drawString(10*cm, y, "Descuento:")
        c.drawString(15*cm, y, f"-Bs. {sale.discount:.2f}")
        y = y - 0.5*cm
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10*cm, y, "TOTAL:")
    c.drawString(15*cm, y, f"Bs. {sale.total:.2f}")
    
    # Pago
    if not sale.is_quotation:
        y = y - 1*cm
        c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, f"Método de Pago: {sale.get_payment_method_display()}")
        c.drawString(2*cm, y - 0.5*cm, f"Monto Pagado: Bs. {sale.amount_paid:.2f}")
        c.drawString(2*cm, y - 1*cm, f"Vuelto: Bs. {sale.change_amount:.2f}")
    
    # Pie de página
    y = 2*cm
    c.setFont("Helvetica", 8)
    if sale.is_quotation:
        c.drawString(2*cm, y, "Esta cotización tiene una validez de 7 días")
        c.drawString(2*cm, y - 0.5*cm, "Los precios están sujetos a cambio sin previo aviso")
    else:
        c.drawString(2*cm, y, "¡Gracias por su compra!")
    
    c.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf