"""
Unidades, modelos
"""

from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class Unidad(database.Model, UniversalMixin):
    """Unidad"""

    # Nombre de la tabla
    __tablename__ = "unidades"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    nombre: Mapped[str] = mapped_column(String(256))
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    # ventanillas: Mapped[List["Ventanilla"]] = relationship(back_populates="unidad")
    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="unidad")

    @property
    def clave_nombre(self):
        """Junta clave y nombre de la unidad"""
        return self.clave + " - " + self.nombre

    def __repr__(self):
        """Representación"""
        return f"<Unidad {self.id}>"
