"""
Usuarios_Turnos_Tipos, modelos
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lib.universal_mixin import UniversalMixin
from tauro.extensions import database


class UsuarioTurnoTipo(database.Model, UniversalMixin):
    """UsuarioTurnoTipo"""

    # Nombre de la tabla
    __tablename__ = "usuarios_turnos_tipos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="usuarios_turnos_tipos")
    turno_tipo_id: Mapped[int] = mapped_column(ForeignKey("turnos_tipos.id"))
    turno_tipo: Mapped["TurnoTipo"] = relationship(back_populates="usuarios_turnos_tipos")

    # Columnas
    es_activo: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        """Representación"""
        return f"<Usuario_Turno_Tipo {self.id}>"
