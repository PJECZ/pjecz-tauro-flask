"""
API-KEY v1 Endpoint: Consultar Unidades
"""

from flask_restful import Resource

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import ListUnidadesOut, UnidadOut
from tauro.blueprints.unidades.models import Unidad


class ConsultarUnidades(Resource):
    """Consultar las Unidades"""

    @api_key_required
    def get(self) -> ListUnidadesOut:
        """Consultar las Unidades"""

        # Consultar
        unidades = (
            Unidad.query.filter_by(es_activo=True)
            .filter_by(estatus="A")
            .filter(Unidad.clave != "ND")
            .order_by(Unidad.nombre)
            .all()
        )

        # Entregar JSON
        return ListUnidadesOut(
            success=True,
            message="Se han consultado las unidades",
            data=[UnidadOut(id=unidad.id, nombre=unidad.nombre, clave=unidad.clave) for unidad in unidades],
        ).model_dump()
