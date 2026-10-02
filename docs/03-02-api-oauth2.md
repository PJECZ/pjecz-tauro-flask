# 🪪 API-OAuth2 v1

API para el ***frontend*** (recepcionistas) y las pantallas públicas. Convenciones generales, objetos comunes y WebSocket: [03-apis.md](03-apis.md). API para sistemas de gestión: [03-01-api-key.md](03-01-api-key.md).

- **Prefijo:** `/api_oauth2/v1` (en producción, `https://<dominio>/admin/api_oauth2/v1`)
- **Autenticación:** `Authorization: Bearer <token>`, obtenido en [`POST /token`](#post-token). Algunos endpoints de lectura son [públicos](#get-consultar_turnos) 🔓.
- **Identidad:** sale del token (`sub` = email); **no** se envía `usuario_id`.
- **Formato:** JSON (`Content-Type: application/json`).

## 📑 Índice

| Operación | Endpoint | Sección |
|-----------|----------|---------|
| Obtener token | `POST /token` | [ir](#post-token) |
| Validar token | `GET /validar_token` | [ir](#get-validar_token) |
| Crear turno | `POST /crear_turno` | [ir](#post-crear_turno) |
| Tomar turno | `GET /tomar_turno` | [ir](#get-tomar_turno) |
| Cambiar estado de un turno | `POST /actualizar_turno_estado` | [ir](#post-actualizar_turno_estado) |
| Actualizar usuario | `POST /actualizar_usuario` | [ir](#post-actualizar_usuario) |
| Consultar configuración del usuario | `GET /consultar_configuracion_usuario` | [ir](#get-consultar_configuracion_usuario) |
| Consultar turnos (todos) 🔓 | `GET /consultar_turnos` | [ir](#get-consultar_turnos) |
| Consultar turnos de una unidad 🔓 | `GET /consultar_turnos/<unidad_id>` | [ir](#get-consultar_turnosunidad_id) |
| Catálogos (estados, tipos, unidades, ubicaciones) | `GET /consultar_*` | [ir](#catálogos-get) |

Además: [vigencia y errores del token](#-vigencia-y-errores-del-token) · [ejemplo completo](#-ejemplo-completo)

## ⏱️ Vigencia y errores del token

| HTTP | `message` | Causa |
|:----:|-----------|-------|
| 401 | "No hay token en esta solicitud" | Falta la cabecera `Authorization: Bearer …` |
| 401 | "No es válido el token!" | Token alterado o mal formado |
| 200 | "El token ha expirado!" (`success: false`) | Pasó la vigencia; hay que pedir otro en `/token` |

> [!WARNING]
> El JWT dura **1 hora** (`exp` fijo en [`autenticar.py`](../tauro/blueprints/api_oauth2_v1/endpoints/autenticar.py)), aunque `/token` responda `expires_in` con `TOKEN_OAUTH2_EXPIRES_IN_SEG` (1 día por defecto). El *frontend* debe renovar según la hora real. Fíjate también en que un token expirado responde **200**, no 401.

---

### `POST /token`

Entrega el token JWT. No requiere autenticación.

**Recibe** (formulario `username`/`password` o JSON con las mismas claves):

```json
{ "username": "recepcion@pjecz.gob.mx", "password": "Ejemplo123" }
```

- `username`: email válido.
- `password`: al menos 8 caracteres, con una letra y un número.
- El usuario debe tener `es_acceso_frontend` y un rol activo.

**Regresa** (`success: true`):

```json
{
  "success": true,
  "message": "Token generado",
  "access_token": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 86400,
  "username": "recepcion@pjecz.gob.mx",
  "usuario_nombre_completo": "Nombre Apellido Apellido",
  "rol":       { "id": 1, "nombre": "…" },
  "unidad":    { "id": 2, "clave": "…", "nombre": "…" },
  "ubicacion": { "id": 3, "nombre": "…", "numero": 1 }
}
```

**Errores** (`success: false`, HTTP 200): "Username y password son requeridos", "Email no válido", "La contraseña debe tener al menos 8 caracteres, una letra y un número", "Usuario no encontrado", "Contraseña incorrecta", "El usuario no tiene acceso al front-end", "El usuario no tiene un rol asignado".

---

### `GET /validar_token`

Sin cuerpo; recibe `Authorization: Bearer <token>`. Regresa `success: true` si el token es vigente, o `success: false` con "No hay token en esta solicitud", "El token ha expirado!" o "No es válido el token!" (siempre HTTP 200).

---

### `POST /crear_turno`

Crea un turno **EN ESPERA** en la unidad indicada, con la ubicación `NO DEFINIDO`. El usuario sale del token.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `turno_tipo_id` | int | sí | Tipo de turno |
| `unidad_id` | int | sí | Unidad a la que va dirigido |
| `turno_telefono` | string | no | Teléfono del ciudadano; se valida y normaliza |
| `comentarios` | string | no | Texto libre (máx. 512) |

```json
{ "turno_tipo_id": 2, "unidad_id": 3, "turno_telefono": "8441234567", "comentarios": "Trae cita" }
```

**Regresa** un [Turno](03-apis.md#objetos-comunes) en `data`. El número es consecutivo **por día**. Se emite por Socket.IO.

**Errores**: "Usuario no encontrado", "Tipo de turno no encontrado", "Unidad no encontrada", "Número de teléfono inválido".

---

### `GET /tomar_turno`

Toma el siguiente turno de la unidad del usuario del token. **Sin cuerpo.**

**Regla**: primer turno `EN ESPERA` de la unidad del usuario, entre los tipos de turno que tenga activos, ordenado por tipo y luego por número. Pasa a `PASE A UBICACION`; se le asigna usuario y ubicación y se registra `inicio`.

**Regresa** el [Turno](03-apis.md#objetos-comunes) tomado. `message`: "Turno 12 tomado por Nombre…". Se emite por Socket.IO y se anuncia en el voceo si la unidad es voceable.

**Errores**: "Usuario no encontrado", "No ha elegido los tipos de turnos que atenderá", **"No hay turnos en espera"**, "Estado de turno no encontrado".

> [!NOTE]
> Es un `GET` que **modifica datos**. Cuida que no lo cachee ni lo repita un navegador, proxy o *prefetch*.

---

### `POST /actualizar_turno_estado`

Cambia el estado de un turno y, opcionalmente, su cubículo.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `turno_id` | int | sí | Turno a modificar |
| `turno_estado_id` | int | sí | Nuevo estado (ver [catálogos](#catálogos-get)) |
| `turno_numero_cubiculo` | int | no | Cubículo a mostrar en pantalla |

```json
{ "turno_id": 40, "turno_estado_id": 4, "turno_numero_cubiculo": 2 }
```

**Regresa** el [Turno](03-apis.md#objetos-comunes) actualizado. `message`: "Se ha cambiado el turno 12 a ATENDIENDO por <email>". Se emite por Socket.IO.

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

Define dónde está el usuario del token y qué tipos de turno atiende.

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|:-----------:|-------------|
| `ubicacion_id` | int | sí | Ventanilla/cubículo (la ubicación `NO DEFINIDO` la libera) |
| `turnos_tipos_ids` | int[] | sí | Tipos que atenderá; los demás se desactivan |

```json
{ "ubicacion_id": 3, "turnos_tipos_ids": [1, 2] }
```

**Regresa** la [Configuración de usuario](03-apis.md#objetos-comunes) actualizada. `message`: "Usuario actualizado".

**Errores**: "Usuario no encontrado", "Ubicacion no encontrada", "Ubicacion eliminada", "Ubicacion no activa", **"Ubicacion ocupada por <nombre>"** (excepto `NO DEFINIDO`).

> [!NOTE]
> Esta configuración se restablece cada madrugada por el [CLI](05-operacion-y-mantenimiento.md#-tareas-programadas-cron); cada jornada el recepcionista debe volver a elegir ubicación y tipos.

---

### `GET /consultar_configuracion_usuario`

Sin cuerpo.

**Regresa** la [Configuración de usuario](03-apis.md#objetos-comunes) del usuario del token. Aquí `ultimo_turno` se busca en estados `EN ESPERA` o `PASE A VENTANILLA`.

> [!WARNING]
> `PASE A VENTANILLA` no se usa en el resto del código (`PASE A UBICACION`), así que `ultimo_turno` probablemente nunca coincida con un turno ya tomado. La [API-Key](03-01-api-key.md#post-consultar_configuracion_usuario) usa otros estados. Conviene revisarlo en [`consultar_configuracion_usuario.py`](../tauro/blueprints/api_oauth2_v1/endpoints/consultar_configuracion_usuario.py).

**Errores**: "Usuario no encontrado o email duplicado", "El usuario no tiene un rol asignado".

---

### `GET /consultar_turnos`

🔓 **Sin autenticación**, a propósito: la usan las pantallas públicas. Sin cuerpo.

Devuelve los turnos activos que no están `COMPLETADO` ni `CANCELADO`, primero los `EN ESPERA` y luego el resto, por número, hasta `LIMITE_DE_TURNOS_LISTADOS`.

**Regresa**:

```json
{ "success": true, "message": "Se han consultado todos los turnos",
  "data": { "ultimo_turno": { "…Turno…" }, "turnos": [ { "…Turno…" } ] } }
```

Sin turnos: `success: true`, `message: "No hay turnos en espera"` y sin `data`.

---

### `GET /consultar_turnos/<unidad_id>`

🔓 **Sin autenticación**. Igual que el anterior, pero filtrado por la unidad de la URL (p. ej. `/consultar_turnos/2`, la misma que muestra `/pantalla/2`).

**Regresa**:

```json
{ "success": true, "message": "Se han consultado los turnos de U02",
  "data": { "unidad": { "id": 2, "clave": "U02", "nombre": "…" },
            "ultimo_turno": { "…Turno…" }, "turnos": [ { "…Turno…" } ] } }
```

**Errores**: "Unidad no encontrada". Sin turnos: `success: true`, "No hay turnos en espera".

---

### Catálogos (`GET`)

Requieren token; sin cuerpo; `data` es una **lista**.

| Ruta | Elemento de la lista |
|------|----------------------|
| `/consultar_turnos_estados` | `{ "id", "nombre" }` |
| `/consultar_turnos_tipos` | `{ "id", "nombre", "nivel" }` |
| `/consultar_unidades` | `{ "id", "clave", "nombre" }` |
| `/consultar_ubicaciones` | `{ "id", "nombre", "numero" }` (solo activas) |

---

## 🧪 Ejemplo completo

```bash
BASE=https://<dominio>/admin/api_oauth2/v1

# 1. Obtener el token (no guardes la contraseña en el historial: usa read -s)
read -rsp "Contraseña: " PASS; echo
TOKEN=$(curl -s -X POST $BASE/token -H "Content-Type: application/json" \
  -d "{\"username\": \"recepcion@pjecz.gob.mx\", \"password\": \"$PASS\"}" | jq -r .access_token)

# 2. Elegir ubicación y tipos de turno
curl -X POST $BASE/actualizar_usuario \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"ubicacion_id": 3, "turnos_tipos_ids": [1, 2]}'

# 3. Tomar el siguiente turno
curl -H "Authorization: Bearer $TOKEN" $BASE/tomar_turno

# 4. Consultar los turnos de la pantalla de la unidad 2 (público)
curl $BASE/consultar_turnos/2
```

Más ejemplos en la colección [Bruno](../tests/bruno) del repositorio.
