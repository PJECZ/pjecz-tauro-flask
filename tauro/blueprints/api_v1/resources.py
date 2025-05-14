"""
API v1 Resources
"""

from flask import Blueprint
from flask_restful import Api

from tauro.blueprints.api_v1.endpoints.actualizar_usuario import ActualizarUsuario
from tauro.blueprints.api_v1.endpoints.autenticar import Authenticate
from tauro.blueprints.api_v1.endpoints.cambiar_turno_estado import CambiarTurnoEstado
from tauro.blueprints.api_v1.endpoints.consultar_turnos import ConsultarTurnos
from tauro.blueprints.api_v1.endpoints.consultar_turnos_tipos import ConsultarTurnosTipos
from tauro.blueprints.api_v1.endpoints.consultar_turnos_unidad import ConsultarTurnosUnidad
from tauro.blueprints.api_v1.endpoints.consultar_ventanilla import ConsultarVentanilla
from tauro.blueprints.api_v1.endpoints.consultar_ventanillas_activas import ConsultarVentanillasActivas
from tauro.blueprints.api_v1.endpoints.crear_turno import CrearTurno
from tauro.blueprints.api_v1.endpoints.tomar_turno import TomarTurno

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

api = Api(api_v1)


api.add_resource(ActualizarUsuario, "/actualizar_usuario")
api.add_resource(Authenticate, "/token")
api.add_resource(CambiarTurnoEstado, "/cambiar_turno_estado")
api.add_resource(ConsultarTurnos, "/consultar_turnos")
api.add_resource(ConsultarTurnosUnidad, "/consultar_turnos/<string:unidad_clave>")
api.add_resource(ConsultarTurnosTipos, "/consultar_turnos_tipos")
api.add_resource(ConsultarVentanilla, "/consultar_ventanilla")
api.add_resource(ConsultarVentanillasActivas, "/consultar_ventanillas_activas")
api.add_resource(CrearTurno, "/crear_turno")
api.add_resource(TomarTurno, "/tomar_turno")
