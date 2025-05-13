"""
API v1 Resources
"""

from flask import Blueprint
from flask_restful import Api, Resource

from tauro.blueprints.api_v1.endpoints.actualizar_usuario import ActualizarUsuario
from tauro.blueprints.api_v1.endpoints.autenticar import Authenticate
from tauro.blueprints.api_v1.endpoints.cambiar_turno_estado import CambiarTurnoEstado
from tauro.blueprints.api_v1.endpoints.consultar_turnos import ConsultarTurnos
from tauro.blueprints.api_v1.endpoints.consultar_turnos_tipos import ConsultarTurnosTipos
from tauro.blueprints.api_v1.endpoints.consultar_ventanilla import ConsultarVentanilla
from tauro.blueprints.api_v1.endpoints.consultar_ventanillas_activas import ConsultarVentanillasActivas
from tauro.blueprints.api_v1.endpoints.crear_turno import CrearTurno
from tauro.blueprints.api_v1.endpoints.tomar_turno import TomarTurno

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

api = Api(api_v1)


class HelloWorld(Resource):
    """Endpoint de prueba"""

    def get(self):
        return {"hello": "world"}


api.add_resource(HelloWorld, "/hello")
api.add_resource(Authenticate, "/token")
api.add_resource(ConsultarTurnosTipos, "/turnos_tipos")
api.add_resource(ConsultarVentanillasActivas, "/ventanillas/consultar_activas")
api.add_resource(ConsultarVentanilla, "/ventanilla")
api.add_resource(CrearTurno, "/turnos/crear")
api.add_resource(CambiarTurnoEstado, "/turnos/cambiar_estado")
api.add_resource(ConsultarTurnos, "/turnos")
api.add_resource(TomarTurno, "/turnos/tomar")
api.add_resource(ActualizarUsuario, "/usuarios/actualizar")
