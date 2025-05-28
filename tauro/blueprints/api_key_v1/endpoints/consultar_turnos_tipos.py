"""
API-Key v1 Endpoint: Consultar Turnos Tipos
"""

from flask_restful import Resource

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import ListTurnosTiposOut, TurnoTipoOut
from tauro.blueprints.turnos_tipos.models import TurnoTipo


class ConsultarTurnosTipos(Resource):
    """Consultar los tipos de turnos"""

    @api_key_required
    def get(self) -> ListTurnosTiposOut:
        """Consultar los tipos de turnos"""

        # Consultar
        turnos_tipos = TurnoTipo.query.filter_by(es_activo=True).filter_by(estatus="A").order_by(TurnoTipo.nombre).all()

        # Entregar JSON
        return ListTurnosTiposOut(
            success=True,
            message="Se han consultado los tipos de turnos",
            data=[
                TurnoTipoOut(id=turno_tipo.id, nombre=turno_tipo.nombre, nivel=turno_tipo.nivel) for turno_tipo in turnos_tipos
            ],
        ).model_dump()
