"""
API v1 Schemas
"""

from pydantic import BaseModel

# ConfigDict
# model_config = ConfigDict(from_attributes=True)


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


class TurnoSchemaOut(BaseModel):
    """Esquema para entregar un turno"""

    id: int
    numero: int
    comentarios: str | None


class VentanillaUsuarioSchemaOut(BaseModel):
    """Esquema para entregar una ventanilla de un usuario"""

    nombre: str
    turnos_tipos_nombres: list[str] | None
    usuario_nombre_completo: str
    ultimo_turno: TurnoSchemaOut | None


class OneVentanillaUsuarioSchemaOut(ResponseSchema):
    """Esquema para entregar una ventanilla de un usuario"""

    data: VentanillaUsuarioSchemaOut


class TurnoSchemaIn(BaseModel):
    """Esquema para crear un turno"""

    turno_tipo_nombre: str
    unidad_clave: str
    comentarios: str | None


class OneTurnoSchemaOut(ResponseSchema):
    """Esquema para entregar un turno ya creado"""

    data: TurnoSchemaOut


class VentanillaActivaOut(BaseModel):
    """Esquema para entregar una ventanilla activa"""

    id: int
    nombre: str


class VentanillasActivasOut(ResponseSchema):
    """Esquema para entregar una lista de ventanillas activas"""

    data: list[VentanillaActivaOut]


class TipoTurnoOut(BaseModel):
    """Esquema para entregar un tipo de turno"""

    nombre: str


class TiposTurnosOut(ResponseSchema):
    """Esquema para entregar una lista de tipos de turnos"""

    data: list[TipoTurnoOut]
