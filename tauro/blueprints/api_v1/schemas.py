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
