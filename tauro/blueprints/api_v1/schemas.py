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


class VentanillaOut(BaseModel):
    """Esquema para entregar una ventanilla"""

    id: int
    nombre: str
    numero: int | None


class ListVentanillasOut(ResponseSchema):
    """Esquema para entregar una lista de ventanillas activas"""

    data: list[VentanillaOut]


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
    turno_comentarios: str | None
    ventanilla: VentanillaOut | None
    unidad: UnidadOut | None


class ConfiguracionUsuarioOut(BaseModel):
    """Esquema para entregar una ventanilla de un usuario"""

    ventanilla: VentanillaOut | None
    unidad: UnidadOut | None
    rol: RolOut | None = None
    turnos_tipos: list[TurnoTipoOut] | None
    usuario_nombre_completo: str
    ultimo_turno: TurnoOut | None


class OneConfiguracionUsuarioOut(ResponseSchema):
    """Esquema para entregar una ventanilla de un usuario"""

    data: ConfiguracionUsuarioOut | None = None


class OneTurnoOut(ResponseSchema):
    """Esquema para entregar un turno ya creado"""

    data: TurnoOut | None = None
