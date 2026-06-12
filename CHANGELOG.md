# 📝 Historial de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [1.3.0] - 2026-06-12 (Aún en desarrollo)

### ✨ Mejoras

- Las unidades ahora incluyen un campo nuevo para indicar cómo pronunciarlo.
- Nuevo estado de turno añadido: `ATENDIENDO EN CUBICULO`.
- Añade vocear cuando el estado del turno es pasar a un cubículo. "PASE A VENTANILLA", "ATENDIENDO EN CUBICULO".
- Añade personalización de CORS por variables de entorno.
- Actualización de la integración con el sistema voceador. En `api-key` y `api-oauth2`.
- Se muestra el número de versión del proyecto en la vista admin.

### ✏️ Cambios

- Se cambio el estado del turno: `PASE A VENTANILLA` a `PASE A UBICACION`.

### 🐞 Arreglado

- Enviar el último turno al cambiar el estado de un turno en el _endpoint_ API-Key `consultar_configuracion_usuario`.
- Quitar del voceador cuando se cambien a ciertos estados el turno. "ATENDIENDO", "EN ESPERA DE CUBICULO", "CANCELADO", "COMPLETADO".

### ⚙️ Requerimiento

- Ejecutar SQL:
  - Añadir campo nuevo `pronunciacion` a la tabla `unidades`: `v1.3.0-01-add-campo-unidades.sql`.
- Añadir nuevos tipos de estado turnos: `PASE A UBICACION` = 7, `PASE A CUBICULO` = 8.


## [1.2.0] - 2026-06-05

### ✨ Mejoras

- Conexión con servicio de voceo.
- Incluir los turnos en estado de ATENDIENDO en el último turno.
- Añadido servicio de voceador. Se envía un mensaje al sistema de voceo o se puede indicar que lo quite de la cola de mensajes voceados.
- Se añadió un estado nuevo para turnos 'PASE A VENTANILLA' entre el estado 'EN ESPERA' y 'ATENDIENDO'. Servirá para que cuando el turno se crea (EN ESPERA) y un cliente del PJECZ tome el turno, este pase a 'PASE A VENTANILLA'. Cuando llegue el cliente, el usuario presionará otro botón y el estado pasará ahora a 'ATENDIENDO'.

### ⚙️ Requerimientos

- Variables de entorno:
  - `VOCEADOR_API_KEY`: Es la API-Key para autentificarse con el sistema voceador.
  - `VOCEADOR_API_KEY_URL`: Es la URL de la API del sistema voceador.


## [1.1.0] - 2026-05-29

### ✨ Mejoras

- Creación de turno de prueba por API-Key.
- Prueba de conexión por API-Key.


## [1.0.0] - 2026-01-09

### ✨ Mejoras

  - Aumentar el tiempo de vida del token en la api oauth2.
