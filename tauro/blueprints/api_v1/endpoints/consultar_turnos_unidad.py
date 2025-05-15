"""
API v1 Endpoint: Consultar Turnos Unidad
"""

from flask_restful import Resource
from sqlalchemy import or_

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import ListTurnosOut, TurnoOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnosUnidad(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

    @token_required
    def get(self, unidad_id: int) -> ListTurnosOut:
        """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

        # Validar el ID de la unidad
        unidad = Unidad.query.get(unidad_id)
        if unidad is None:
            return ListTurnosOut(
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
            .order_by(TurnoTipo.nombre, Turno.numero)
            .all()
        )

        # Si no se encuentran turnos, entregar success en verdadero
        if not turnos:
            return ListTurnosOut(
                success=True,
                message="No hay turnos en espera",
            ).model_dump()

        # Entregar JSON
        return ListTurnosOut(
            success=True,
            message=f"Se han consultado los turnos de {unidad.clave}",
            data=[TurnoOut(id=turno.id, numero=turno.numero, comentarios=turno.comentarios) for turno in turnos],
        ).model_dump()
