# 📚 Documentación de PJECZ-Tauro (Sistema de Turnos)

Documentación técnica del _backend_ **pjecz-tauro-flask**. Está pensada para quien va a **mantener, desplegar o integrarse** con el sistema.

> [!NOTE]
> Los diagramas están escritos en [Mermaid](https://mermaid.js.org/), así que GitHub los muestra directamente. El mapa interactivo de las dos APIs está en [diagrama-operación.html](diagrama-operación.html); ábrelo en el navegador.

## 🗺️ Índice

| #   | Documento                                                        | Contenido                                                                        |
| --- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 1   | [Visión general y arquitectura](01-arquitectura.md)              | Qué es Tauro, componentes, rutas públicas, flujo de un turno                     |
| 2   | [Base de datos](02-base-de-datos.md)                             | Diagrama entidad-relación y descripción de las tablas                            |
| 3   | [APIs](03-apis.md)                                               | API-Key (sistemas de gestión) y API-OAuth2 (_frontend_), _endpoints_ y WebSocket |
| 3.1 | [API-Key v1](03-01-api-key.md)                                   | Índice y detalle de cada _endpoint_ para sistemas de gestión                     |
| 3.2 | [API-OAuth2 v1](03-02-api-oauth2.md)                             | Índice y detalle de cada _endpoint_ para el _frontend_ y las pantallas           |
| 4   | [Instalación y configuración](04-instalacion-y-configuracion.md) | Variables de entorno, instalación, arranque, servicio systemd, nginx             |
| 5   | [Operación y mantenimiento](05-operacion-y-mantenimiento.md)     | Tareas programadas, CLI, respaldos, despliegue, scripts del servidor             |

## 📦 Archivos de apoyo en esta carpeta

Son copias de los archivos que viven en el servidor.

| Archivo                                                | Ubicación en el servidor      | Para qué sirve                                        |
| ------------------------------------------------------ | ----------------------------- | ----------------------------------------------------- |
| [pjecz-tauro.service](pjecz-tauro.service)             | `/etc/systemd/system/`        | Servicio systemd del _backend_                        |
| [tauro-turnos.nginx](tauro-turnos.nginx)               | `/etc/nginx/sites-available/` | Sitio de nginx (_frontend_, `/admin/`, `/socket.io/`) |
| [cli-turnos.sh](cli-turnos.sh)                         | `~/.local/bin/`               | Cancela los turnos pendientes de días anteriores      |
| [cli-usuarios.sh](cli-usuarios.sh)                     | `~/.local/bin/`               | Restablece asignaciones de los usuarios               |
| [20-actualizar-proyecto.sh](20-actualizar-proyecto.sh) | `~/.bashrc.d/`                | Función `actualizar-proyecto-tauro`                   |
| [90-pantalla-bienvenida.sh](90-pantalla-bienvenida.sh) | `~/.bashrc.d/`                | Pantalla de bienvenida con los comandos disponibles   |
| [bash_aliases](bash_aliases)                           | `~/.bash_aliases`             | Alias `cargar-tauro-flask`, `cli-turnos`, etc.        |
| [diagrama-operación.html](diagrama-operación.html)     | —                             | Mapa interactivo de operación                         |

> [!WARNING]
> **Nunca** guardes en esta carpeta contraseñas, `SECRET_KEY`, `SALT`, API-Keys, IPs internas ni archivos `.env`. Usa siempre valores de ejemplo (`XXXX`), como hace [`.env.example`](../.env.example).
