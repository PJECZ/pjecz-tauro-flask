"""
API-Keys, modelos
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class APIKey(database.Model, UniversalMixin):
    """APIKey"""

    # Nombre de la tabla
    __tablename__ = "api_keys"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    api_key: Mapped[str] = mapped_column(String(128))
    api_key_expiracion: Mapped[datetime]
    es_activo: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        """Representación"""
        return f"<APIKey {self.id}>"
