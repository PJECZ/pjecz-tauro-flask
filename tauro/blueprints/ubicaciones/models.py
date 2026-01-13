"""
Ubicaciones, modelos
"""

from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class Ubicacion(database.Model, UniversalMixin):
    """Ubicación"""

    # Nombre de la tabla
    __tablename__ = "ubicaciones"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256))
    numero: Mapped[Optional[int]] = mapped_column(nullable=True, default=None)
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    turnos: Mapped[List["Turno"]] = relationship(back_populates="ubicacion")
    unidades_ubicaciones: Mapped[List["UnidadUbicacion"]] = relationship(back_populates="ubicacion")
    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="ubicacion")

    @property
    def nombre_numero(self):
        """Junta clave y nombre de la ubicación"""
        if self.numero:
            return f"{self.nombre} - {self.numero}"
        return self.nombre

    def __repr__(self):
        """Representación"""
        return f"<Ubicación {self.id}>"
