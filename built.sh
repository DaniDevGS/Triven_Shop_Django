#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. **Ejecutar migraciones (CRÍTICO)**
python manage.py migrate

# 3. Recolectar archivos estáticos
python manage.py collectstatic --no-input

# 4. 🔥 PASO TEMPORAL: CARGAR LOS DATOS 🔥
# ¡Asegúrate de que el nombre del archivo coincida!
python manage.py loaddata all_data.json