"""
Turnos, modelos
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class Turno(database.Model, UniversalMixin):
    """Turno"""

    # Nombre de la tabla
    __tablename__ = "turnos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="turnos")
    turno_estado_id: Mapped[int] = mapped_column(ForeignKey("turnos_estados.id"))
    turno_estado: Mapped["TurnoEstado"] = relationship(back_populates="turnos")
    turno_tipo_id: Mapped[int] = mapped_column(ForeignKey("turnos_tipos.id"))
    turno_tipo: Mapped["TurnoTipo"] = relationship(back_populates="turnos")
    ventanilla_id: Mapped[int] = mapped_column(ForeignKey("ventanillas.id"))
    ventanilla: Mapped["Ventanilla"] = relationship(back_populates="turnos")

    # Columnas
    numero: Mapped[int]
    inicio: Mapped[Optional[datetime]] = mapped_column(DateTime)
    termino: Mapped[Optional[datetime]] = mapped_column(DateTime)
    unidad_id: Mapped[Optional[int]]
    comentarios: Mapped[Optional[str]] = mapped_column(String(512))

    def __repr__(self):
        """Representación"""
        return f"<Turno {self.id}>"
