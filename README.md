# 🏛️ [pjecz-tauro-flask]

> Aplicación Web para la administración y control de los turnos dentro del PJECZ Ciudad Judicial.
> Proyectos relaccionados:
> - [pjecz-tauro-reactjs](https://github.com/PJECZ/pjecz-tauro-reactjs) (Sistema _Frontend_)
> - [pjecz-columba-cli-typer](https://github.com/ricval/pjecz-columba-cli-typer) (Sistema de Voceo)
> - pjecz-casiopea (Sistema de Citas)

---

## 📖 Descripción General

El sistema contiene la parte web administrativa, que puede administrar los turnos existentes, controlar los usuarios que entran vía web y las API-Keys para los demás sistemas que quieran comunicarse con este.
Hay dos partes tipo API una API-Oauth2 para comunicarse con el _frontend_ y otra tipo API-Key para comunicarse con otros sistemas (los sistemas de gestión).
Puedes crear, tomar, o cambiar el estado a uno ya definido de un turno. El listado de turnos aparece en dos televisiones en el _lobby_ del edificio de ciudad judicial.

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.14
* **Framework:** Flask
* **Base de Datos:** PostgreSQL
* **Servidor:** Nginx
* **Otros:** SocketIO

## ⚙️ Requisitos Previos

Lista de herramientas necesarias para correr el proyecto localmente:
- Git
- Python
- uv - manejador de paquetes para Python

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio:
   ```bash
   git clone https://github.com/PJECZ/pjecz-tauro-flask.git
   cd pjecz-tauro-flask
   ```

### 2. Configurar variables de entorno:
Copia el archivo de ejemplo y edita las credenciales necesarias (Base de datos, API Keys):
```
cp .env.example .env
```

### 3. Instalar dependencias:
```bash
uv sync
```

### 4. Iniciar el servidor de desarrollo:
```bash
uv run flask run --host=0.0.0.0 --port=5020
```

## 🌿 Estructura de Ramas

Este proyecto sigue el flujo de trabajo institucional:
- `main`: Rama de producción (Solo código estable).
- `dev`: Rama de integración y pruebas (_Staging_).
- `feature/*`: Ramas temporales para nuevas funcionalidades.

Ver más sobre como contribuir: [CONTRIBUTING](CONTRIBUTING.md)

## 🚢 Despliegue

Ejecutar comando en servidor de producción después de haber integrado el PR en la rama `dev`:

```bash
actualizar-proyecto-tauro
```

---

## ✉️ Contacto

- **Departamento:** Dirección de Informática - PJECZ
- **Responsable:** Dir. Guillermo Valdés, Carlos Hernández y Ricardo Valdés
- **Email:** [correo@pjecz.gob.mx]

---

© 2026 Poder Judicial del Estado de Coahuila de Zaragoza.
