#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Instalar dependencias
pip install -r requirements.txt

# 3. Recolectar archivos estáticos
python manage.py collectstatic --no-input

# 2. **Ejecutar migraciones (CRÍTICO)**
python manage.py migrate

python manage.py loaddata products_data.json