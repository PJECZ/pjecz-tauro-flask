"""
API-Key v1 Endpoint: Consultar Ubicaciones
"""

from flask_restful import Resource

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import ListUbicacionesOut, UbicacionOut
from tauro.blueprints.ubicaciones.models import Ubicacion


class ConsultarUbicaciones(Resource):
    """Consultar las ubicaciones"""

    @api_key_required
    def get(self) -> ListUbicacionesOut:
        """Consultar las ubicaciones"""

        # Consultar las ubicaciones activas omitiendo la NO DEFINIDO
        ubicaciones = (
            Ubicacion.query.filter_by(es_activo=True)
            .filter_by(estatus="A")
            .filter(Ubicacion.nombre != "NO DEFINIDO")
            .order_by(Ubicacion.nombre)
            .all()
        )

        # Entregar JSON
        return ListUbicacionesOut(
            success=True,
            message="Se han consultado las ubicaciones",
            data=[UbicacionOut(id=ubicacion.id, nombre=ubicacion.nombre, numero=ubicacion.numero) for ubicacion in ubicaciones],
        ).model_dump()
