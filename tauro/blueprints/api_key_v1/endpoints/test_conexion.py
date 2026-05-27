"""
API-Key v1 Endpoint: Test de conexión
"""

from flask_restful import Resource

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import ResponseSchema


class TestConexion(Resource):
    """Test de conexión"""

    @api_key_required
    def get(self):
        """Test de conexión"""
        return ResponseSchema(success=True, message="Conexión exitosa").dict()