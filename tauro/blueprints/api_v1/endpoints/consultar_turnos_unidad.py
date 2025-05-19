"""
API v1 Endpoint: Consultar Turnos Unidad
"""

from flask_restful import Resource
from sqlalchemy import or_

from tauro.blueprints.api_v1.schemas import OneUnidadTurnosOut, TurnoOut, UnidadTurnosOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnosUnidad(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

    def get(self, unidad_id: int) -> OneUnidadTurnosOut:
        """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

        # Validar el ID de la unidad
        unidad = Unidad.query.get(unidad_id)
        if unidad is None:
            return OneUnidadTurnosOut(
                success=False,
                message="Unidad no encontrada",
            ).model_dump()

        # Consultar los turnos...
        # - Filtrar por unidad,
        # - Filtrar por los estados EN ESPERA y ATENDIENDO,
        # - Filtrar por el estatus A (activo),
        # - Y ordenar por el nombre de tipo de turno ATENCION URGENTE, CON CITA, NORMAL y luego por el número del turno
        turnos = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(Turno.unidad_id == unidad.id)
            .filter(or_(TurnoEstado.nombre == "EN ESPERA", TurnoEstado.nombre == "ATENDIENDO"))
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .all()
        )

        # Si no se encuentran turnos, entregar success en verdadero
        if not turnos:
            return OneUnidadTurnosOut(
                success=True,
                message="No hay turnos en espera",
            ).model_dump()

        # Entregar JSON
        return OneUnidadTurnosOut(
            success=True,
            message=f"Se han consultado los turnos de {unidad.clave}",
            data=UnidadTurnosOut(
                unidad_id=unidad.id,
                unidad_clave=unidad.clave,
                unidad_nombre=unidad.nombre,
                turnos=[
                    TurnoOut(
                        turno_id=turno.id,
                        turno_numero=turno.numero,
                        turno_estado=turno.turno_estado.nombre,
                        turno_comentarios=turno.comentarios,
                    )
                    for turno in turnos
                ],
            ),
        ).model_dump()
