"""
API-Key v1 Schemas
"""

from pydantic import BaseModel


class ConsultarUsuarioIn(BaseModel):
    """Esquema para consultar un usuario"""

    usuario_id: int
