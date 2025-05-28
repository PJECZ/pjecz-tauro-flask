"""
API-Key v1 Endpoint: Consultar Ventanillas
"""

from flask_restful import Resource

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import ListVentanillasOut, VentanillaOut
from tauro.blueprints.ventanillas.models import Ventanilla


class ConsultarVentanillas(Resource):
    """Consultar las ventanillas"""

    @api_key_required
    def get(self) -> ListVentanillasOut:
        """Consultar las ventanillas"""

        # Consultar las ventanillas activas omitiendo la NO DEFINIDO
        ventanillas = (
            Ventanilla.query.filter_by(es_activo=True)
            .filter_by(estatus="A")
            .filter(Ventanilla.nombre != "NO DEFINIDO")
            .order_by(Ventanilla.nombre)
            .all()
        )

        # Entregar JSON
        return ListVentanillasOut(
            success=True,
            message="Se han consultado las ventanillas",
            data=[
                VentanillaOut(id=ventanilla.id, nombre=ventanilla.nombre, numero=ventanilla.numero)
                for ventanilla in ventanillas
            ],
        ).model_dump()
