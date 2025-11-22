#! /usr/bin/env bash
# Exit on error
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. **Ejecutar migraciones (CRÍTICO)**
python manage.py migrate

# 3. CREAR SUPERUSUARIO (ADMIN)
# Utiliza las variables de entorno configuradas en Render.
# El comando --no-input es crucial para que no pida interacción.
python manage.py createsuperuser --no-input \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL

# Nota: La contraseña se lee automáticamente de la variable de entorno
# DJANGO_SUPERUSER_PASSWORD cuando se usa --no-input y se proporcionan
# el username y el email.

# 4. Recolectar archivos estáticos
python manage.py collectstatic --no-input

# 5. 🔥 CARGAR LOS DATOS (Si aún es necesario) 🔥
python manage.py loaddata all_data.json

#sss