"""
API-Key v1 Schemas
"""

from pydantic import BaseModel


class ConsultarUsuarioIn(BaseModel):
    """Esquema para consultar un usuario"""

    usuario_id: int


class ActualizarUsuarioIn(BaseModel):
    """Esquema para actualizar un usuario"""

    usuario_id: int
    ventanilla_id: int
    turnos_tipos_ids: list[int]
