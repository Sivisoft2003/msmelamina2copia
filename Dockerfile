FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar código
COPY . .

# 🔥 EJECUTAR EN ESTE ORDEN:
# 1. Recolectar estáticos
RUN python manage.py collectstatic --noinput

# 🔥 2. Primero migrar (crear tablas)
RUN python manage.py migrate

# 🔥 3. Luego crear superusuario (después de las migraciones)
RUN python create_superuser.py

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]