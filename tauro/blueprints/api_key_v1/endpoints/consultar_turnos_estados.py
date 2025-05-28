"""
API-Key v1 Endpoint: Consultar Turnos Estados
"""

from flask_restful import Resource

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import ListTurnosEstadosOut, TurnoEstadoOut
from tauro.blueprints.turnos_estados.models import TurnoEstado


class ConsultarTurnosEstados(Resource):
    """Consultar los estados de los turnos"""

    @api_key_required
    def get(self) -> ListTurnosEstadosOut:
        """Consultar los estados de los turnos"""

        # Consultar
        turnos_tipos = TurnoEstado.query.filter_by(es_activo=True).filter_by(estatus="A").order_by(TurnoEstado.nombre).all()

        # Entregar JSON
        return ListTurnosEstadosOut(
            success=True,
            message="Se han consultado los tipos de turnos",
            data=[TurnoEstadoOut(id=turno_tipo.id, nombre=turno_tipo.nombre) for turno_tipo in turnos_tipos],
        ).model_dump()
