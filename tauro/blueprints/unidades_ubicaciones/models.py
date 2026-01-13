"""
Unidades_Ubicaciones, modelos
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class UnidadUbicacion(database.Model, UniversalMixin):
    """UnidadUbicación"""

    # Nombre de la tabla
    __tablename__ = "unidades_ubicaciones"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    unidad_id: Mapped[int] = mapped_column(ForeignKey("unidades.id"))
    unidad: Mapped["Unidad"] = relationship(back_populates="unidades_ubicaciones")
    ubicacion_id: Mapped[int] = mapped_column(ForeignKey("ubicaciones.id"))
    ubicacion: Mapped["Ubicacion"] = relationship(back_populates="unidades_ubicaciones")

    # Columnas
    es_activo: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        """Representación"""
        return f"<UnidadUbicación {self.id}>"
