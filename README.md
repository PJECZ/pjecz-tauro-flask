# 🏛️ pjecz-tauro-flask

> Aplicación Web para la administración y control de los turnos dentro del PJECZ Ciudad Judicial.
> Proyectos relacionados:
>
> - [pjecz-tauro-reactjs](https://github.com/PJECZ/pjecz-tauro-reactjs) (Sistema _Frontend_)
> - [pjecz-columba-cli-typer](https://github.com/ricval/pjecz-columba-cli-typer) (Sistema de Voceo)
> - pjecz-casiopea (Sistema de Citas)

---

## 📖 Descripción General

El sistema contiene la parte web administrativa, que puede administrar los turnos existentes, controlar los usuarios que entran vía web y las API-Keys para los demás sistemas que quieran comunicarse con este.
Hay dos partes tipo API una API-Oauth2 para comunicarse con el _frontend_ y otra tipo API-Key para comunicarse con otros sistemas (los sistemas de gestión).
Puedes crear, tomar, o cambiar el estado a uno ya definido de un turno. El listado de turnos aparece en dos televisiones en el _lobby_ del edificio de ciudad judicial.

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python 3.14
- **Framework:** Flask
- **Base de Datos:** PostgreSQL
- **Servidor:** Nginx
- **Otros:** Flask-SocketIO, Flask-RESTful, SQLAlchemy 2, gunicorn
- **Dependencias:** uv (el archivo `uv.lock` se versiona)

## ⚙️ Requisitos Previos

Lista de herramientas necesarias para correr el proyecto localmente:

- Git
- Python 3.14 o superior
- PostgreSQL 17 con una base de datos creada para el proyecto
- uv - manejador de paquetes para Python

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio:

```bash
git clone https://github.com/PJECZ/pjecz-tauro-flask.git
cd pjecz-tauro-flask
```

### 2. Configurar variables de entorno:

Copia el archivo de ejemplo y edita las credenciales necesarias (base de datos, `SECRET_KEY`, `SALT`, API-Key del voceador):

```bash
cp .env.example .env
```

> [!WARNING]
> `.env` está en `.gitignore`. Nunca subas credenciales al repositorio.

### 3. Instalar dependencias:

```bash
uv sync
```

### 4. Inicializar la base de datos:

Crea las tablas y carga los catálogos con el CLI (los CSV de carga no se versionan; solicítalos al equipo):

```bash
export PYTHONPATH=$(pwd)
uv run python cli/app.py db --help
```

### 5. Iniciar el servidor de desarrollo:

```bash
uv run flask run --host=0.0.0.0 --port=5020
```

### 6. Pruebas (opcional):

Las pruebas de `tests/` consumen la API en ejecución. Requieren en el `.env` las variables `API_KEY`, `API_BASE_URL`, `TURNOS_TIPOS_IDS`, `UNIDADES_IDS`, `USUARIOS_IDS` y `UBICACIONES_IDS`.

```bash
uv run pytest
```

También hay una colección para el cliente [Bruno](https://www.usebruno.com/) en `tests/bruno/`.

## 📚 Documentación

La documentación técnica está en [`docs/`](docs/README.md):

- [Arquitectura](docs/01-arquitectura.md)
- [Base de datos](docs/02-base-de-datos.md)
- [APIs](docs/03-apis.md)
- [Instalación y configuración](docs/04-instalacion-y-configuracion.md)
- [Operación y mantenimiento](docs/05-operacion-y-mantenimiento.md)

El historial de versiones está en [CHANGELOG](CHANGELOG.md).

## 🌿 Estructura de Ramas

Este proyecto sigue el flujo de trabajo institucional:

- `main`: Rama de producción (solo código estable).
- `dev`: Rama de integración y pruebas (_Staging_).
- `mejora/*`, `fix/*`: Ramas temporales para nuevas funcionalidades o correcciones.

Ver más sobre como contribuir: [CONTRIBUTING](CONTRIBUTING.md)

## 🚢 Despliegue

Ejecutar el comando en el servidor después de haber integrado los cambios en la rama que éste siga (ver [operación](docs/05-operacion-y-mantenimiento.md#-despliegue)):

```bash
actualizar-proyecto-tauro
```

---

## ✉️ Contacto

- **Departamento:** Dirección de Informática - PJECZ
- **Responsable:** Dir. Guillermo Valdés, Carlos Hernández y Ricardo Valdés

---

© 2026 Poder Judicial del Estado de Coahuila de Zaragoza.
