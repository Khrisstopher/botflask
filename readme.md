# Proyecto botflask

Repositorio de un proyecto personal **en desarrollo**, construido con Python y Flask.

## Objetivos principales

Desarrollar una aplicación web con Flask, una base de datos y una interfaz web.

## Estructura del repositorio

- `app/` → Código de la aplicación.
- `tests/` → Pruebas automatizadas.
- `migrations/` → Migraciones de la base de datos gestionadas con Flask-Migrate y Alembic.
- `wsgi.py` → Punto de entrada de la aplicación.
- `requirements.txt` → Dependencias necesarias para ejecutar el proyecto.
- `requirements-dev.txt` → Dependencias adicionales para desarrollo y pruebas.

## Tecnologías utilizadas

- **Backend:** Python 3.14.6, Flask.
- **Frontend:** HTML, CSS, JavaScript, Bootstrap y jQuery.
- **Base de datos:** SQLite en el entorno local, según la configuración.
- **Migraciones:** Flask-Migrate y Alembic.
- **Entorno de desarrollo:** Visual Studio Code y entornos virtuales.

## Cómo instalar y ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/khrisstopher/botflask.git
cd botflask
```

### 2. Crear y activar el entorno virtual

En Windows, desde PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
```

Si vas a ejecutar pruebas o desarrollar el proyecto, instala también las dependencias de desarrollo:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configurar las variables de entorno

Configura las variables que necesite la aplicación, como `SECRET_KEY` y, si corresponde, `DATABASE_URL`.

Consulta `.env.example` si está disponible. No subas archivos `.env` ni credenciales al repositorio.

### 5. Aplicar las migraciones de la base de datos

**Este paso debe ejecutarse antes de crear el usuario administrador.**

```bash
flask --app wsgi db upgrade
```

Este comando aplica las migraciones versionadas en `migrations/` y prepara las tablas de la base de datos configurada.

### 6. Crear el usuario administrador

Una vez aplicadas las migraciones, ejecuta:

```bash
flask --app wsgi crear-admin
```

El comando solicitará el nombre de usuario, el correo electrónico y la contraseña del administrador, salvo que estén configurados mediante las variables de entorno correspondientes.

La contraseña debe cumplir los requisitos de validación de la aplicación.

**Orden obligatorio:**

1. `flask --app wsgi db upgrade`
2. `flask --app wsgi crear-admin`

### 7. Ejecutar la aplicación

Con el entorno virtual activado, ejecuta:

```bash
python wsgi.py
```

Si el proyecto se configura para ejecutarse mediante otro servidor o comando, sigue la configuración correspondiente.

## Base de datos y migraciones

- La carpeta `migrations/` debe estar incluida en Git para que otros desarrolladores puedan aplicar las migraciones existentes.
- Las bases de datos locales y los archivos de la carpeta `instance/` no deben subirse al repositorio.
- Cuando cambie el esquema de los modelos, se deben generar y revisar las migraciones correspondientes antes de aplicarlas.

## Autor

**Cristofer Castro Arias**

- [WhatsApp](https://wa.me/573005352422)
- [YouTube](https://www.youtube.com/@KhrisstopherTube)
- [Email](mailto:moralesk2026@outlook.com)
