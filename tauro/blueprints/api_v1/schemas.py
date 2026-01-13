"""
API v1 Schemas
"""

from pydantic import BaseModel


class ResponseSchema(BaseModel):
    """Esquema común para responder todas las peticiones"""

    success: bool
    message: str
    data: dict | list | None = None


class UnidadOut(BaseModel):
    """Esquema para entregar una Unidad"""

    id: int
    clave: str
    nombre: str


class ListUnidadesOut(ResponseSchema):
    """Esquema para entregar una lista de Unidades"""

    data: list[UnidadOut]


class UbicacionOut(BaseModel):
    """Esquema para entregar una ubicacion"""

    id: int
    nombre: str
    numero: int | None = None


class ListUbicacionesOut(ResponseSchema):
    """Esquema para entregar una lista de ubicaciones activas"""

    data: list[UbicacionOut]


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


class RolOut(BaseModel):
    """Esquema para entregar un rol"""

    id: int
    nombre: str


class TurnoOut(BaseModel):
    """Esquema para entregar un turno"""

    turno_id: int
    turno_numero: int
    turno_fecha: str
    turno_estado: str
    turno_tipo_id: int
    turno_numero_cubiculo: int
    turno_comentarios: str | None = None
    turno_telefono: str | None = None
    ubicacion: UbicacionOut | None = None
    unidad: UnidadOut | None = None


class ConfiguracionUsuarioOut(BaseModel):
    """Esquema para entregar una ubicacion de un usuario"""

    ubicacion: UbicacionOut | None = None
    unidad: UnidadOut | None = None
    rol: RolOut | None = None
    turnos_tipos: list[TurnoTipoOut] | None = None
    usuario_nombre_completo: str
    ultimo_turno: TurnoOut | None = None


class OneConfiguracionUsuarioOut(ResponseSchema):
    """Esquema para entregar una ubicacion de un usuario"""

    data: ConfiguracionUsuarioOut | None = None


class OneTurnoOut(ResponseSchema):
    """Esquema para entregar un turno ya creado"""

    data: TurnoOut | None = None
