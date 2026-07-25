#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias del sistema para Pillow
apt-get update
apt-get install -y python3-dev libjpeg-dev libpng-dev libtiff-dev zlib1g-dev

# Instalar dependencias de Python
pip install --upgrade pip
pip install -r requirements.txt

# Recolectar estáticos
python manage.py collectstatic --noinput

# Migrar
python manage.py migrate