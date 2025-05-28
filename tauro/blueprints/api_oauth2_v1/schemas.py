"""
API-OAuth2 v1 Schemas
"""

from pydantic import BaseModel

from tauro.blueprints.api_v1.schemas import (
    ResponseSchema,
    RolOut,
    TurnoOut,
    UnidadOut,
    VentanillaOut,
)


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
    ventanilla: VentanillaOut | None = None


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
