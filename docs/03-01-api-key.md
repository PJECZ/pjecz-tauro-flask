# 🔑 API-Key v1

API para los **sistemas de gestión** (p. ej. SAJI) que crean turnos, los toman y cambian su estado. Convenciones generales, objetos comunes y WebSocket: [03-apis.md](03-apis.md). API para el *frontend*: [03-02-api-oauth2.md](03-02-api-oauth2.md).

- **Prefijo:** `/api_key/v1` (en producción, `https://<dominio>/admin/api_key/v1`)
- **Autenticación:** cabecera `X-Api-Key: <llave>`
- **Identidad:** el usuario va en el cuerpo (`usuario_id`); la llave identifica al **sistema**, y su `nombre` queda en la bitácora.
- **Formato:** JSON (`Content-Type: application/json`).

## 📑 Índice

| Operación | Endpoint | Sección |
|-----------|----------|---------|
| Probar conexión | `GET /test_conexion` | [ir](#get-test_conexion) |
| Crear turno | `POST /crear_turno` | [ir](#post-crear_turno) |
| Crear turno de prueba | `POST /test_crear_turno` | [ir](#post-test_crear_turno) |
| Tomar turno | `POST /tomar_turno` | [ir](#post-tomar_turno) |
| Cambiar estado de un turno | `POST /actualizar_turno_estado` | [ir](#post-actualizar_turno_estado) |
| Actualizar usuario | `POST /actualizar_usuario` | [ir](#post-actualizar_usuario) |
| Consultar configuración del usuario | `POST /consultar_configuracion_usuario` | [ir](#post-consultar_configuracion_usuario) |
| Catálogos (estados, tipos, unidades, ubicaciones) | `GET /consultar_*` | [ir](#catálogos-get) |

Además: [errores de autenticación](#-errores-de-autenticación) · [ejemplo completo](#-ejemplo-completo) · [gestión de llaves](#-gestión-de-llaves)

## 🚫 Errores de autenticación

| HTTP | `message` | Causa |
|:----:|-----------|-------|
| 401 | "Falta el API key" | No se envió `X-Api-Key` |
| 401 | "El API key no es válido o no existe" | Llave desconocida o borrada |
| 403 | "El API key está deshabilitado" | `es_activo = false` en la tabla `api_keys` |

Los errores de negocio responden HTTP 200 con `success: false` (ver [convenciones](03-apis.md#convenciones)).

---

### `GET /test_conexion`

Valida la llave y la red. Sin cuerpo.

**Regresa**: `{ "success": true, "message": "Conexión exitosa" }`

---

### `POST /crear_turno`

Crea un turno **EN ESPERA** en la unidad indicada, con la ubicación `NO DEFINIDO`.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `usuario_id` | int | sí | Usuario que genera el turno |
| `turno_tipo_id` | int | sí | Tipo de turno |
| `unidad_id` | int | sí | Unidad a la que va dirigido |
| `turno_telefono` | string | no | Teléfono del ciudadano; se valida y normaliza |
| `comentarios` | string | no | Texto libre (máx. 512) |

```json
{ "usuario_id": 5, "turno_tipo_id": 2, "unidad_id": 3, "turno_telefono": "8441234567", "comentarios": "Trae cita" }
```

**Regresa** un [Turno](03-apis.md#objetos-comunes) en `data`. `message`: "Se ha creado el turno 12 en U01 por Nombre…". El número es consecutivo **por día**. Se emite por Socket.IO.

**Errores**: "Usuario no encontrado", "Tipo de turno no encontrado", "Unidad no encontrada", "Número de teléfono inválido".

---

### `POST /test_crear_turno`

Mismo cuerpo que [`crear_turno`](#post-crear_turno); sirve para pruebas de integración.

---

### `POST /tomar_turno`

Toma el siguiente turno de la unidad del usuario.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `usuario_id` | int | sí | Usuario que atiende |

```json
{ "usuario_id": 7 }
```

**Regla**: primer turno `EN ESPERA` de la unidad del usuario, entre los tipos de turno que tenga activos, ordenado por tipo y luego por número. Pasa a `PASE A UBICACION`; se le asigna usuario y ubicación y se registra `inicio`.

**Regresa** el [Turno](03-apis.md#objetos-comunes) tomado. `message`: "Turno 12 tomado por Nombre…". Se emite por Socket.IO y se anuncia en el voceo si la unidad es voceable.

**Errores**: "Usuario no encontrado", "No ha elegido los tipos de turnos que atenderá", **"No hay turnos en espera"**, "Estado de turno no encontrado".

---

### `POST /actualizar_turno_estado`

Cambia el estado de un turno y, opcionalmente, su cubículo.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `usuario_id` | int | sí | Usuario que hace el cambio |
| `turno_id` | int | sí | Turno a modificar |
| `turno_estado_id` | int | sí | Nuevo estado (ver [catálogos](#catálogos-get)) |
| `turno_numero_cubiculo` | int | no | Cubículo a mostrar en pantalla |

```json
{ "usuario_id": 7, "turno_id": 40, "turno_estado_id": 4, "turno_numero_cubiculo": 2 }
```

**Regresa** el [Turno](03-apis.md#objetos-comunes) actualizado. `message`: "Se ha actualizado información del turno 12 por el usuario …". Se emite por Socket.IO.

**Efecto en el voceo**:

| Nuevo estado | Voceo |
|--------------|-------|
| `PASE A UBICACION`, `PASE A CUBICULO` | Se **agrega** el anuncio (si la unidad es voceable) |
| `EN ESPERA DE CUBICULO`, `ATENDIENDO`, `ATENDIENDO EN CUBICULO`, `CANCELADO`, `COMPLETADO` | Se **quita** el anuncio |

> [!NOTE]
> Los fallos del servicio de voceo se ignoran: el cambio se guarda y la respuesta es exitosa aunque el anuncio no salga.

**Errores**: "Usuario no encontrado", "Turno no encontrado", "Estado de turno no encontrado".

---

### `POST /actualizar_usuario`

Define dónde está el usuario y qué tipos de turno atiende.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `usuario_id` | int | sí | Usuario a actualizar |
| `ubicacion_id` | int | sí | Ventanilla/cubículo (la ubicación `NO DEFINIDO` la libera) |
| `turnos_tipos_ids` | int[] | sí | Tipos que atenderá; los demás se desactivan |

```json
{ "usuario_id": 7, "ubicacion_id": 3, "turnos_tipos_ids": [1, 2] }
```

**Regresa** la [Configuración de usuario](03-apis.md#objetos-comunes) actualizada. `message`: "Usuario actualizado".

**Errores**: "Usuario no encontrado", "Ubicacion no encontrada", "Ubicacion eliminada", "Ubicacion no activa", **"Ubicacion ocupada por <nombre>"** (excepto `NO DEFINIDO`).

> [!NOTE]
> Esta configuración se restablece cada madrugada por el [CLI](05-operacion-y-mantenimiento.md#-tareas-programadas-cron).

---

### `POST /consultar_configuracion_usuario`

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `usuario_id` | int | sí | Usuario a consultar |

```json
{ "usuario_id": 7 }
```

**Regresa** la [Configuración de usuario](03-apis.md#objetos-comunes). Aquí `ultimo_turno` es el turno del usuario en estado `ATENDIENDO`, `ATENDIENDO EN CUBICULO`, `PASE A UBICACION` o `PASE A CUBICULO`.

**Errores**: "Usuario no encontrado", "El usuario no tiene un rol asignado".

---

### Catálogos (`GET`)

Sin cuerpo; `data` es una **lista**. Usa los `id` devueltos en los demás endpoints.

| Ruta | Elemento de la lista |
|------|----------------------|
| `/consultar_turnos_estados` | `{ "id", "nombre" }` |
| `/consultar_turnos_tipos` | `{ "id", "nombre", "nivel" }` |
| `/consultar_unidades` | `{ "id", "clave", "nombre" }` |
| `/consultar_ubicaciones` | `{ "id", "nombre", "numero" }` (solo activas) |

```json
{ "success": true, "message": "…", "data": [ { "id": 1, "nombre": "NORMAL", "nivel": 3 } ] }
```

---

## 🧪 Ejemplo completo

```bash
BASE=https://<dominio>/admin/api_key/v1
KEY=<tu-api-key>            # nunca la dejes en el historial ni en el repositorio

# 1. Verificar conexión
curl -H "X-Api-Key: $KEY" $BASE/test_conexion

# 2. Crear un turno
curl -X POST $BASE/crear_turno \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"usuario_id": 5, "turno_tipo_id": 2, "unidad_id": 3}'

# 3. Tomar el siguiente turno de la unidad del usuario 7
curl -X POST $BASE/tomar_turno \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"usuario_id": 7}'
```

Más ejemplos en la colección [Bruno](../tests/bruno) del repositorio.

## 🔐 Gestión de llaves

Se administran desde el módulo **API Keys** del sitio o desde el CLI:

```bash
uv run python cli/app.py usuarios nueva-api-key correo@pjecz.gob.mx --dias 90
uv run python cli/app.py usuarios mostrar-api-key correo@pjecz.gob.mx
```

Requieren `PYTHONPATH` apuntando a la raíz del proyecto (ver [operación](05-operacion-y-mantenimiento.md)). Cada llave nace **deshabilitada** (`es_activo = false`) y expira en `api_key_expiracion`; ponle un `nombre` descriptivo para identificarla en la bitácora.
