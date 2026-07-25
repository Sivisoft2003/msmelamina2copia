from django.core.management.base import BaseCommand
from apps.products.tag_utils import actualizar_tags_productos

class Command(BaseCommand):
    help = 'Actualiza las etiquetas automáticas de los productos'
    
    def handle(self, *args, **options):
        """Método que se ejecuta cuando llamas al comando"""
        self.stdout.write('🔄 Actualizando etiquetas automáticas...')
        
        try:
            # Ejecutar la función que actualiza las etiquetas
            actualizar_tags_productos()
            self.stdout.write(self.style.SUCCESS('✅ Etiquetas actualizadas correctamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))