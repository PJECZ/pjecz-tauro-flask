"""
turnos, modelos
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class Turno(database.Model, UniversalMixin):
    """ Turno """

    ESTADOS = {
        "EN_ESPERA": "En Espera",
        "ATENDIENDO": "Atendiendo",
        "COMPLETADO": "Completado",
    }

    TIPOS = {
        "NORMAL": "Normal",
        "CON_CITA": "Con Cita",
        "DISCAPACIDAD": "Discapacidad",
        "URGENTE": "Urgente",
    }

    # Nombre de la tabla
    __tablename__ = 'turnos'

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="turnos")
    ventanilla_id: Mapped[int] = mapped_column(ForeignKey("ventanillas.id"))
    ventanilla: Mapped["Ventanilla"] = relationship(back_populates="turnos")

    # Columnas
    numero: Mapped[int]
    turno_solicitado: Mapped[str] = mapped_column(String(512))  # Es el ID del sistema externo que hace la petición de creación de un nuevo turno
    tipo: Mapped[str] = mapped_column(Enum(*TIPOS, name="turnos_tipos", native_enum=False), index=True)
    inicio: Mapped[datetime] = mapped_column(DateTime, default=now())
    termino: Mapped[datetime] = mapped_column(DateTime, default=now())
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="turnos_estados", native_enum=False), index=True)
    comentarios: Mapped[Optional[str]] = mapped_column(String(512))

    def __repr__(self):
        """ Representación """
        return f'<Turno {self.id}>'
