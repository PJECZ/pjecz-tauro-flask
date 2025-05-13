"""
API v1 Endpoint: Consultar Turnos
"""

from flask_restful import Resource
from sqlalchemy import or_

from lib.safe_string import safe_string
from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import ListTurnoSchemaOut, TurnoSchemaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo


class ConsultarTurnos(Resource):
    """Consultar turnos"""

    @token_required
    def get(self) -> ListTurnoSchemaOut:
        """Consultar turnos"""
        # Consultar los turnos "EN ESPERA" y "ATENDIENDO",
        # ordenados por el nombre del tipo de turno "ATENCION URGENTE", "CON CITA", "NORMAL"
        # y el número del turno, de menor a mayor
        turnos = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(or_(TurnoEstado.nombre == "EN ESPERA", TurnoEstado.nombre == "ATENDIENDO"))
            .order_by(TurnoTipo.nombre, Turno.numero)
            .all()
        )
        # TODO: Si viene la unidad se va a filtrar por unidad
        # Entregar JSON
        return ListTurnoSchemaOut(
            success=True,
            message="Se han consultado todos los turnos",
            data=[TurnoSchemaOut(id=turno.id, numero=turno.numero, comentarios=turno.comentarios) for turno in turnos],
        ).model_dump()
