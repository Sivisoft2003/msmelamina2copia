import sys
import os

# Ruta de tu proyecto en PythonAnywhere
# 🔥 CAMBIA "tunombreusuario" por tu usuario de PythonAnywhere
path = '/home/sivisoft/msmelamina2copia'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
