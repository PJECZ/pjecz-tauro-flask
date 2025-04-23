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
    """ Unidad """

    # Nombre de la tabla
    __tablename__ = 'unidades'

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    nombre: Mapped[str] = mapped_column(String(256))

    # Hijos
    ventanillas: Mapped[List["Ventanilla"]] = relationship(back_populates="unidades")

    def __repr__(self):
        """ Representación """
        return f'<Unidad {self.id}>'
