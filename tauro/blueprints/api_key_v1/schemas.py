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
