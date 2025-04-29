"""
API-Keys, modelos
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class API_Key(database.Model, UniversalMixin):
    """API_Key"""

    # Nombre de la tabla
    __tablename__ = "api_keys"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    api_key: Mapped[Optional[str]] = mapped_column(String(128))
    api_key_expiracion: Mapped[Optional[datetime]]
    es_activo: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        """Representación"""
        return f"<API_Key {self.id}>"
