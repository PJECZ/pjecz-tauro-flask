"""
Ventanillas, modelos
"""

from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class Ventanilla(database.Model, UniversalMixin):
    """Ventanilla"""

    # Nombre de la tabla
    __tablename__ = "ventanillas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[Optional[str]] = mapped_column(String(256))
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="ventanilla")

    def __repr__(self):
        """Representación"""
        return f"<Ventanilla {self.id}>"
