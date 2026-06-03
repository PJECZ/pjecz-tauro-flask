# 📝 Historial de Cambios (Changelog)

Todos los cambios notables en este proyecto serán documentados en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [1.2.0] - 2026-06-05

### ✨ Mejoras

- Mientras el estado del turno se encuentre el 'PASE A VENTANILLA' será voceado por el sistema de voceo.
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
