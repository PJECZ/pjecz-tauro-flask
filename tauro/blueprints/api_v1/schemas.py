"""
API v1 Schemas
"""

from pydantic import BaseModel, ConfigDict


class ResponseSchema(BaseModel):
    """Esquema común para responder todas las peticiones"""

    success: bool
    message: str
    data: dict | list | None = None


class TurnoSchemaOut(BaseModel):
    """Esquema para entregar un Turno"""

    id: int
    numero: int
    unidad_id: int | None
    comentarios: str | None
    model_config = ConfigDict(from_attributes=True)


class TurnoSchemaIn(BaseModel):
    """Esquema para generar un nuevo turno"""

    usuario_email: str
    turno_tipo_nombre: str
    unidad_clave: str
    comentarios: str | None


class TomarTurnoSchemaIn(BaseModel):
    """Esquema para tomar un turno"""

    usuario_email: str
    turno_estado_nombre: str
    turno_tipo_nombre: str
    ventanilla_id: int
    unidad_id: int | None
    comentarios: str | None
