"""
API v1 Schemas
"""

from pydantic import BaseModel


class ResponseSchema(BaseModel):
    """Esquema común para responder todas las peticiones"""

    success: bool
    message: str
    data: dict | list | None = None


class RolOut(BaseModel):
    """Esquema para entregar un rol"""

    id: int
    nombre: str


class UnidadOut(BaseModel):
    """Esquema para entregar una Unidad"""

    id: int
    clave: str
    nombre: str


class ListUnidadesOut(ResponseSchema):
    """Esquema para entregar una lista de Unidades"""

    data: list[UnidadOut]


class TokenSchema(BaseModel):
    """Esquema para entregar el token"""

    success: bool
    message: str
    access_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None
    username: str | None = None
    usuario_nombre_completo: str | None = None
    rol: RolOut | None = None
    unidad: UnidadOut | None = None


class TurnoEstadoOut(BaseModel):
    """Esquema para entregar un estado de turno"""

    id: int
    nombre: str


class ListTurnosEstadosOut(ResponseSchema):
    """Esquema para entregar una lista de estados de turnos"""

    data: list[TurnoEstadoOut]


class TurnoTipoOut(BaseModel):
    """Esquema para entregar un tipo de turno"""

    id: int
    nombre: str
    nivel: int


class ListTurnosTiposOut(ResponseSchema):
    """Esquema para entregar una lista de tipos de turnos"""

    data: list[TurnoTipoOut]


class VentanillaOut(BaseModel):
    """Esquema para entregar una ventanilla"""

    id: int
    nombre: str
    numero: int | None


class TurnoOut(BaseModel):
    """Esquema para entregar un turno"""

    turno_id: int
    turno_numero: int
    turno_estado: str
    turno_comentarios: str | None
    ventanilla: VentanillaOut | None


class UnidadTurnosOut(BaseModel):
    """Esquema para entregar una unidad con sus turnos"""

    unidad: UnidadOut
    ultimo_turno: TurnoOut | None
    turnos: list[TurnoOut] | None


class TurnoUnidadOut(BaseModel):
    """Esquema para entregar un turno"""

    turno_id: int
    turno_numero: int
    turno_estado: str
    turno_comentarios: str | None
    unidad: UnidadOut
    ventanilla: VentanillaOut | None


class OneUnidadTurnosOut(ResponseSchema):
    """Esquema para entregar una unidad con sus turnos"""

    data: UnidadTurnosOut | None = None


class VentanillaActivaOut(BaseModel):
    """Esquema para entregar una ventanilla activa"""

    id: int
    nombre: str
    numero: int | None


class ListVentanillasActivasOut(ResponseSchema):
    """Esquema para entregar una lista de ventanillas activas"""

    data: list[VentanillaActivaOut]


class VentanillaUsuarioOut(BaseModel):
    """Esquema para entregar una ventanilla de un usuario"""

    ventanilla: VentanillaOut | None
    unidad: UnidadOut | None
    rol: RolOut | None = None
    turnos_tipos: list[TurnoTipoOut] | None
    usuario_nombre_completo: str
    ultimo_turno: TurnoOut | None


class OneVentanillaUsuarioOut(ResponseSchema):
    """Esquema para entregar una ventanilla de un usuario"""

    data: VentanillaUsuarioOut | None = None


class CrearTurnoIn(BaseModel):
    """Esquema para crear un turno"""

    turno_tipo_id: int
    unidad_id: int
    comentarios: str | None


class OneTurnoOut(ResponseSchema):
    """Esquema para entregar un turno ya creado"""

    data: TurnoOut | None = None


class ListTurnosOut(BaseModel):
    """Esquema para entregar un listado de todos los turnos"""

    ultimo_turno: TurnoUnidadOut | None = None
    turnos: list[TurnoUnidadOut] | None = None


class OneListTurnosOut(ResponseSchema):
    """Esquema para entregar un listado de Turnos"""

    data: ListTurnosOut | None = None


class ActualizarTurnoEstadoIn(BaseModel):
    """Esquema para cambiar el estado de un turno"""

    turno_id: int  # Turno ID
    turno_estado_id: int  # Turno Estado ID


class ActualizarUsuarioIn(BaseModel):
    """Esquema para actualizar un usuario"""

    ventanilla_id: int
    turnos_tipos_ids: list[int]
