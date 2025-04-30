"""
Unidades_Ventanillas, modelos
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class UnidadVentanilla(database.Model, UniversalMixin):
    """UnidadVentanilla"""

    # Nombre de la tabla
    __tablename__ = "unidades_ventanillas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    unidad_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"))
    unidad: Mapped["Unidad"] = relationship(back_populates="unidades_ventanillas")
    ventanilla_id: Mapped[int] = mapped_column(ForeignKey("ventanillas.id"))
    ventanilla: Mapped["Ventanilla"] = relationship(back_populates="unidades_ventanillas")

    # Columnas
    es_activo: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        """Representación"""
        return f"<UnidadVentanilla {self.id}>"
