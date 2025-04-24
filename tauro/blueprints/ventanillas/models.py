"""
Ventanillas, modelos
"""

from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class Ventanilla(database.Model, UniversalMixin):
    """Ventanilla"""

    # Nombre de la tabla
    __tablename__ = "ventanillas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="ventanillas")
    # unidad_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"))
    # unidad: Mapped["Unidad"] = relationship(back_populates="ventanillas")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    es_habilitada: Mapped[bool] = mapped_column(default=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(256))

    # Hijos
    # turnos: Mapped[List["Turno"]] = relationship(back_populates="ventanillas")

    def __repr__(self):
        """Representación"""
        return f"<Ventanilla {self.id}>"
