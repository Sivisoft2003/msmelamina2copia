FROM python:3.10-slim

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema (necesario para Pillow)
RUN apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput

# Exponer el puerto (el que usa Render)
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
