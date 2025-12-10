# 🛒 Triven Smart Shop - Plataforma E-commerce de Alto Rendimiento

[![Status Proyecto](https://img.shields.io/badge/Estado-Producci%C3%B3n%20Ready-brightgreen)](https://github.com/DaniDevGS/Triven_Shop_Django)
[![Hecho con Django](https://img.shields.io/badge/Framework-Django%204+-092E20?logo=django)](https://www.djangoproject.com/)
[![Licencia](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<img src="./products/static/img/Logo_Triven.png" alt="Triven Logo" width="300">

## 📌 Introducción

**Triven Smart Shop** es una plataforma de comercio electrónico (e-commerce) diseñada para la venta de productos importados en Venezuela. Este proyecto sirve como una **demostración exhaustiva de habilidades FullStack** utilizando la arquitectura **Modelo-Vista-Plantilla (MTV)** de Django, con un enfoque en la escalabilidad, la seguridad y una experiencia de usuario completamente *responsive*.

Este sistema está diseñado para manejar la lógica de negocio completa de un *e-commerce*, desde la gestión de inventario y pedidos hasta la integración de pagos.

## ✨ Características Destacadas

Hemos implementado un conjunto de características robustas y técnicas clave:

* **Sistema de Gestión de Pedidos:**
    * Flujo de compra completo con carritos de sesión y persistencia en DB.
    * Visualización detallada de estados de pedidos: **Pendiente de Pago**, **Procesando**, **Enviado**, **Completado** y **Rechazado**.
* **Diseño *Mobile-First***: Interfaz desarrollada con **Tailwind CSS** para una experiencia 100% *responsive* en dispositivos móviles.
* **Autenticación Personalizada:** Uso del `AbstractUser` de Django para una gestión de usuarios flexible y escalable.
* **Control de Inventario:** Gestión de *stock* con **transacciones atómicas** para asegurar la integridad de los datos durante las compras concurrentes.
* **Base de Datos Relacional:** Uso de **PostgreSQL** para la persistencia de datos, ofreciendo robustez y rendimiento.
* **Seguridad:** Implementación de medidas de seguridad estándar de Django (CSRF, XSS) y manejo seguro de variables de entorno.

## 💻 Stack Tecnológico (FullStack)

El proyecto está segmentado en componentes clave utilizando tecnologías modernas:

| Componente | Tecnología | Versión | Propósito |
| :--- | :--- | :--- | :--- |
| **Backend/Core** | [![Python](https://skillicons.dev/icons?i=py)](https://www.python.org/) & [![Django](https://skillicons.dev/icons?i=django)](https://www.djangoproject.com/) | 3.10+ / 4+ | Lógica de negocio, APIs internas y motor de plantillas. |
| **Base de Datos** | [![PostgreSQL](https://skillicons.dev/icons?i=postgresql)](https://www.postgresql.org/) | 14+ | Almacenamiento transaccional de productos, usuarios y pedidos. |
| **Frontend/UI** | [![HTML](https://skillicons.dev/icons?i=html)](https://developer.mozilla.org/en-US/docs/Web/HTML) & [![Tailwind CSS](https://skillicons.dev/icons?i=tailwindcss)](https://tailwindcss.com/) | Latest | Estructura, diseño y optimización de la experiencia de usuario. |
| **Manejo de Pagos** | *[PENDIENTE DE INTEGRAR]* | N/A | (Si planeas agregar una pasarela de pago como Stripe o Mercado Pago, menciónalo aquí). |

## 🖼️ Demostración Visual



*Aquí deberías incluir un **GIF o Capturas de Pantalla** que muestren:*
1.  *La página de inicio con productos.*
2.  *El proceso de agregar al carrito.*
3.  *La vista de gestión de pedidos del usuario.*

## ⚙️ Instalación y Ejecución Local

Sigue estos pasos para levantar el sitio web en tu entorno de desarrollo local.

### 1. Prerrequisitos

* **Python 3.10+**
* **`pip`** (Python package installer)
* **Una instancia de PostgreSQL** (o configura para usar SQLite si es solo para pruebas locales rápidas).

### 2. Clonar el Repositorio

```bash
git clone [https://github.com/DaniDevGS/Triven_Shop_Django.git](https://github.com/DaniDevGS/Triven_Shop_Django.git)
cd Triven_Shop_Django
```
### 3. Configuración del Entorno
Es crucial usar un entorno virtual para gestionar las dependencias:

```bash
# Crear el entorno virtual (venv)
python -m venv venv

# Activar el entorno virtual
# En Windows:
.\venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate

# Instalar las dependencias del proyecto
pip install -r requirements.txt
```

### 4. Configuración de Base de Datos y Migraciones

Antes de ejecutar el servidor, debes configurar tu base de datos y aplicar las migraciones:

1. Crea un archivo .env en el directorio raíz basado en un archivo de ejemplo (.env.example - asegúrate de incluir uno en tu repo).

2. Aplica las migraciones de Django para crear el esquema de la base de datos:

```bash
python manage.py makemigrations 
python manage.py migrate
```

### 5. Ejecutar la Aplicación
Finalmente, inicia el servidor de desarrollo de Django:

```bash
python manage.py runserver
```

El sitio estará accesible en http://127.0.0.1:8000/

## 📜 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo LICENSE para más detalles.