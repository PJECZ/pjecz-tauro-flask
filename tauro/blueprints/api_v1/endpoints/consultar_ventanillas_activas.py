"""
API v1 Endpoint: Consultar Ventanillas Activas
"""

from flask_restful import Resource

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import ListVentanillasActivasOut, VentanillaActivaOut
from tauro.blueprints.ventanillas.models import Ventanilla


class ConsultarVentanillasActivas(Resource):
    """Consultar las ventanillas activas"""

    @token_required
    def get(self) -> ListVentanillasActivasOut:
        """Consultar las ventanillas activas"""

        # Consultar
        ventanillas = Ventanilla.query.filter_by(es_activo=True).filter_by(estatus="A").order_by(Ventanilla.nombre).all()

        # Entregar JSON
        return ListVentanillasActivasOut(
            success=True,
            message="Se han consultado las ventanillas activas",
            data=[VentanillaActivaOut(id=ventanilla.id, nombre=ventanilla.nombre) for ventanilla in ventanillas],
        ).model_dump()
