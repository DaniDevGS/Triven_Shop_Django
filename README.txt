# Triven Smart Shop

<img src="./products/static/img/Logo_Triven.png" alt="Triven Logo" width="300">

Este proyecto es sitio web de ventas digitales (e-commerce) de productos importados a Venezuela para la empresa Triven. El proyecto fue echo con Django usando su arquitectura **Modelo-Plantilla-Vista (MTV)**, un proyecto que muestra mis habilidades FullStack.

## Caracteristicas

* Permite la compra de productos.

* Visualiacion de compras realizadas exitosamente, compras pendientes y compras rechazadas por el sistema.

* Guardado de datos en una base de datos

* Interfaz completamente responsive principalmente en moviles

## Stack Tecnológico

---
| Componente | Tecnología | Propósito |
| :--- | :---| :--- |
| **Backend** | [![Backend](https://skillicons.dev/icons?i=py,django)](https://github.com/DaniDevGS/Demon-Slayer-API)| Controlador y principal cerebro de la logica del sitio web. |
| **Base de Datos** | [![DB](https://skillicons.dev/icons?i=postgresql)](https://github.com/DaniDevGS/Demon-Slayer-API) | Modelo, lugar de almacenamiento de los datos. |
| **Frontend** | [![My Skills](https://skillicons.dev/icons?i=html,css,tailwindcss,js)](https://github.com/DaniDevGS/Demon-Slayer-API) | Vista. |
---

## Instalación y Ejecución

Sigue estos pasos para levantar el sitio web en tu entorno local.

### Prerequisitos

* **Python 3+**
* **`pip`** (Python package installer)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/DaniDevGS/Triven_Shop_Django.git
cd Triven_Shop_Django
```

### 2. Crear Entorno Virtual e Instalar Dependencias

Se recomienda usar un entorno virtual para aislar las dependencias del proyecto.

```bash

# Crear entorno virtual (ej. venv)
python -m venv venv

# Activar el entorno virtual
# En Windows:
.\venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate

# Instalar los requisitos del sitio web
pip pip install -r requirements.txt
```
### 3. Ejecutar la Aplicación
Ejecuta el servidor de Django

```bash
python manage.py runserver
```
