"""
API v1 Schemas
"""

from pydantic import BaseModel


class ResponseSchema(BaseModel):
    """Esquema común para responder todas las peticiones"""

    success: bool
    message: str
    data: dict | list | None = None


class TokenSchema(BaseModel):
    """Esquema para entregar el token"""

    success: bool
    message: str
    access_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None
    username: str | None = None


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


class ListTurnosTiposOut(ResponseSchema):
    """Esquema para entregar una lista de tipos de turnos"""

    data: list[TurnoTipoOut]


class TurnoOut(BaseModel):
    """Esquema para entregar un turno"""

    id: int
    numero: int
    comentarios: str | None


class VentanillaActivaOut(BaseModel):
    """Esquema para entregar una ventanilla activa"""

    id: int
    nombre: str


class ListVentanillasActivasOut(ResponseSchema):
    """Esquema para entregar una lista de ventanillas activas"""

    data: list[VentanillaActivaOut]


class VentanillaUsuarioOut(BaseModel):
    """Esquema para entregar una ventanilla de un usuario"""

    id: int  # Ventanilla ID
    ventanilla: str  # Ventanilla nombre
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


class ListTurnosOut(ResponseSchema):
    """Esquema para entregar un turno ya creado"""

    data: list[TurnoOut] | None = None


class ActualizarTurnoEstadoIn(BaseModel):
    """Esquema para cambiar el estado de un turno"""

    id: int  # Turno ID
    turno_estado_id: int  # Turno Estado ID


class ActualizarUsuarioIn(BaseModel):
    """Esquema para actualizar un usuario"""

    ventanilla_id: int
    turnos_tipos_ids: list[int]
