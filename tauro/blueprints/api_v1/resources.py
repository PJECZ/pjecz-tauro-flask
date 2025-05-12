"""
API v1 Resources
"""

from flask import Blueprint, request
from flask_restful import Api, Resource
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from lib.safe_string import safe_string
from tauro.blueprints.api_v1.schemas import ResponseSchema, TurnoSchemaIn, TurnoSchemaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.ventanillas.models import Ventanilla

api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")

api = Api(api_v1)


class HelloWorld(Resource):
    """Endpoint de prueba"""

    def get(self):
        return {"hello": "world"}


class ConsultarVentanilla(Resource):
    """Consultar ventanilla del usuario"""

    def get(self):
        """Consultar ventanilla del usuario"""
        # Entregar
        # - ventanilla
        # - tipos de turnos del usuario
        # - nombre completo del usuario
        # - ultimo turno
        return ResponseSchema(
            success=True,
            message="Se ha consultado la ventanilla",
            data=None,
        ).model_dump()


class CambiarTurnoEstado(Resource):
    """Cambiar estado del turno"""

    def post(self):
        """Cambiar estado del turno"""
        # Recibir
        # - id del turno
        # - nuevo estado
        return ResponseSchema(
            success=True,
            message="Se ha cambiado el estado del turno",
            data=None,
        ).model_dump()


class TomarTurno(Resource):
    """Tomar un turno"""

    def get(self):
        """Tomar un turno"""
        return ResponseSchema(
            success=True,
            message="Se ha tomado el turno",
            data=None,
        ).model_dump()


class ConsultarTurnos(Resource):
    """Consultar los turnos"""

    def get(self, unidad_id=None):
        """Consultar los turnos"""
        # Consultar turnos activos
        turnos = Turno.query.order_by(Turno.id.desc()).all()
        # Serializar
        turnos_serializados = [TurnoSchemaOut.model_validate(turno) for turno in turnos]
        # Entregar JSON
        return ResponseSchema(
            success=True,
            message="Se han consultado los turnos",
            data=turnos_serializados,
        ).model_dump()


class CrearTurno(Resource):
    """Crear un turno"""

    def post(self):
        """Generar nuevo turno"""
        # Obtener datos del request
        data = request.get_json()
        # Validar datos
        turno_in = TurnoSchemaIn.model_validate(data)
        # Consultar el usuario a partir del email
        try:
            usuario = Usuario.query.filter_by(email=turno_in.usuario_email).one()
        except (MultipleResultsFound, NoResultFound):
            return ResponseSchema(
                success=False,
                message="Usuario no encontrado o email duplicado",
            ).model_dump()
        # Consultar el tipo de turno
        try:
            turno_tipo = TurnoTipo.query.filter_by(nombre=turno_in.turno_tipo_nombre).one()
        except (MultipleResultsFound, NoResultFound):
            return ResponseSchema(
                success=False,
                message="Tipo de turno no encontrado o nombre duplicado",
            ).model_dump()
        # Consultar la unidad
        try:
            unidad = Unidad.query.filter_by(clave=turno_in.unidad_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return ResponseSchema(
                success=False,
                message="Unidad no encontrada o clave duplicada",
            ).model_dump()
        # Consultar el estado de turno
        try:
            turno_estado = TurnoEstado.query.filter_by(nombre="EN ESPERA").one()
        except (MultipleResultsFound, NoResultFound):
            return ResponseSchema(
                success=False,
                message="Estado de turno no encontrado o nombre duplicado",
            ).model_dump()
        # Consultar la ventanilla NO DEFINIDO
        try:
            ventanilla = Ventanilla.query.filter_by(nombre="NO DEFINIDO").one()
        except (MultipleResultsFound, NoResultFound):
            return ResponseSchema(
                success=False,
                message="Ventanilla no encontrada o nombre duplicado",
            ).model_dump()
        # Consultar el numero de turno
        numero = Turno.query.count() + 1
        # Crear nuevo turno
        nuevo_turno = Turno(
            usuario=usuario,
            turno_estado_id=turno_estado.id,
            turno_tipo=turno_tipo,
            ventanilla=ventanilla,
            numero=numero,
            unidad_id=unidad.id,
            comentarios=safe_string(turno_in.comentarios, max_len=500, save_enie=True),
        )
        # Guardar en la base de datos
        nuevo_turno.save()
        # Serializar
        data = TurnoSchemaOut(
            id=nuevo_turno.id,
            numero=nuevo_turno.numero,
            unidad_id=nuevo_turno.unidad_id,
            turno_estado_nombre=nuevo_turno.turno_estado_nombre,
            comentarios=nuevo_turno.comentarios,
        ).model_dump()
        # Entregar JSON
        return ResponseSchema(
            success=True,
            message="Turno generado",
            data=data,
        ).model_dump()


class ConsultarVentanillasActivas(Resource):
    """Consultar ventanillas activas"""


class ConsultarTurnosTipos(Resource):
    """Consultar tipos de turnos"""


class ActualizarUsuario(Resource):
    """Actualizar usuario"""


api.add_resource(HelloWorld, "/hello")
api.add_resource(ConsultarVentanilla, "/ventanilla")
api.add_resource(CambiarTurnoEstado, "/turnos/cambiar_estado")
api.add_resource(TomarTurno, "/turnos/tomar")
api.add_resource(ConsultarTurnos, "/turnos")
api.add_resource(ConsultarVentanillasActivas, "/ventanillas/consultar_activas")
api.add_resource(ConsultarTurnosTipos, "/turnos_tipos")
api.add_resource(ActualizarUsuario, "/usuarios/actualizar")
