"""
API v1 Endpoint: Consultar Turnos Tipos
"""

from flask_restful import Resource

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import TiposTurnosOut, TipoTurnoOut
from tauro.blueprints.turnos_tipos.models import TurnoTipo


class ConsultarTurnosTipos(Resource):
    """Consultar tipos de turnos"""

    @token_required
    def get(self) -> TiposTurnosOut:
        """Consultar tipos de turnos"""
        # Consultar
        turnos_tipos = TurnoTipo.query.filter_by(es_activo=True).order_by(TurnoTipo.nombre).all()
        # Serializar
        data = [TipoTurnoOut(nombre=turno_tipo.nombre) for turno_tipo in turnos_tipos]
        # Entregar JSON
        return TiposTurnosOut(
            success=True,
            message="Se han consultado los tipos de turnos",
            data=data,
        ).model_dump()
