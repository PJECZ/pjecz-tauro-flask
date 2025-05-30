"""
Ventanillas, modelos
"""

from typing import List, Optional

from sqlalchemy import String
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
    nombre: Mapped[str] = mapped_column(String(256))
    numero: Mapped[Optional[int]] = mapped_column(nullable=True, default=None)
    es_activo: Mapped[bool] = mapped_column(default=True)

    # Hijos
    turnos: Mapped[List["Turno"]] = relationship(back_populates="ventanilla")
    unidades_ventanillas: Mapped[List["UnidadVentanilla"]] = relationship(back_populates="ventanilla")
    usuarios: Mapped[List["Usuario"]] = relationship(back_populates="ventanilla")

    @property
    def nombre_numero(self):
        """Junta clave y nombre de la ventanilla"""
        if self.numero:
            return f"{self.nombre} - {self.numero}"
        return self.nombre

    def __repr__(self):
        """Representación"""
        return f"<Ventanilla {self.id}>"
