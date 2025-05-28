"""
API Key v1 Resources
"""

from flask import Blueprint
from flask_cors import CORS
from flask_restful import Api

from config.settings import get_settings

# from tauro.blueprints.api_key_v1.endpoints.actualizar_turno_estado import ActualizarTurnoEstado
# from tauro.blueprints.api_key_v1.endpoints.actualizar_usuario import ActualizarUsuario
# from tauro.blueprints.api_key_v1.endpoints.autenticar import Authenticate, ValidarToken
# from tauro.blueprints.api_key_v1.endpoints.consultar_configuracion_usuario import ConsultarConfiguracionUsuario
# from tauro.blueprints.api_key_v1.endpoints.consultar_turnos import ConsultarTurnos
# from tauro.blueprints.api_key_v1.endpoints.consultar_turnos_estados import ConsultarTurnosEstados
# from tauro.blueprints.api_key_v1.endpoints.consultar_turnos_tipos import ConsultarTurnosTipos
# from tauro.blueprints.api_key_v1.endpoints.consultar_turnos_unidad import ConsultarTurnosUnidad
from tauro.blueprints.api_key_v1.endpoints.consultar_unidades import ConsultarUnidades

# from tauro.blueprints.api_key_v1.endpoints.consultar_ventanillas_activas import ConsultarVentanillasActivas
# from tauro.blueprints.api_key_v1.endpoints.crear_turno import CrearTurno
# from tauro.blueprints.api_key_v1.endpoints.tomar_turno import TomarTurno

api_key_v1 = Blueprint("api_key_v1", __name__, url_prefix="/api_key/v1")

# Crear la API
api = Api(api_key_v1)

# CORS
CORS(api_key_v1)
origins = ["http://localhost:5000", "http://127.0.0.1:5000"]
settings = get_settings()
if settings.HOST:
    origins.append(settings.HOST)
CORS(api_key_v1, origins=origins)

# Agregar los recursos a la API
# api.add_resource(Authenticate, "/token")
# api.add_resource(ActualizarTurnoEstado, "/actualizar_turno_estado")
# api.add_resource(ActualizarUsuario, "/actualizar_usuario")
# api.add_resource(ConsultarTurnos, "/consultar_turnos")
# api.add_resource(ConsultarTurnosEstados, "/consultar_turnos_estados")
# api.add_resource(ConsultarTurnosTipos, "/consultar_turnos_tipos")
# api.add_resource(ConsultarTurnosUnidad, "/consultar_turnos/<int:unidad_id>")
# api.add_resource(ConsultarConfiguracionUsuario, "/consultar_configuracion_usuario")
api.add_resource(ConsultarUnidades, "/consultar_unidades")
# api.add_resource(ConsultarVentanillasActivas, "/consultar_ventanillas_activas")
# api.add_resource(CrearTurno, "/crear_turno")
# api.add_resource(TomarTurno, "/tomar_turno")
# api.add_resource(ValidarToken, "/validar_token")
