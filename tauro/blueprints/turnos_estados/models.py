"""
Turnos_Estados, modelos
"""

from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class Turno_Estado(database.Model, UniversalMixin):
    """Turno_Estado"""

    # Nombre de la tabla
    __tablename__ = "turnos_estados"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256), unique=True)
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    turnos: Mapped[List["Turno"]] = relationship(back_populates="turno_estado")

    def __repr__(self):
        """Representación"""
        return f"<Turno_Estado {self.id}>"
