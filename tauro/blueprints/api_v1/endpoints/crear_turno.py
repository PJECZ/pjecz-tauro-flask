"""
API v1 Endpoint: Crear Turno
"""

from flask import g, request
from flask_restful import Resource
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from lib.safe_string import safe_string
from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import OneTurnoSchemaOut, TurnoSchemaIn, TurnoSchemaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.ventanillas.models import Ventanilla


class CrearTurno(Resource):
    """Crear un nuevo turno"""

    @token_required
    def post(self) -> OneTurnoSchemaOut:
        """Crear un turno"""
        # Consultar el usuario
        username = g.current_user
        try:
            usuario = Usuario.query.filter_by(email=username).one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoSchemaOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()
        # Recibir y validar TurnoSchemaIn
        payload = request.get_json()
        turno_in = TurnoSchemaIn.model_validate(payload)
        # Consultar el tipo de turno
        try:
            turno_tipo = TurnoTipo.query.filter_by(nombre=turno_in.turno_tipo_nombre).one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoSchemaOut(
                success=False,
                message="Tipo de turno no encontrado",
            ).model_dump()
        # Consultar la unidad
        try:
            unidad = Unidad.query.filter_by(clave=turno_in.unidad_clave).one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoSchemaOut(
                success=False,
                message="Unidad no encontrada",
            ).model_dump()
        # Consultar el estado de turno "EN ESPERA"
        try:
            turno_estado = TurnoEstado.query.filter_by(nombre="EN ESPERA").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoSchemaOut(
                success=False,
                message="Estado de turno no encontrado",
            ).model_dump()
        # Consultar la ventanilla NO DEFINIDO
        try:
            ventanilla = Ventanilla.query.filter_by(nombre="NO DEFINIDO").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoSchemaOut(
                success=False,
                message="Ventanilla no encontrada",
            ).model_dump()
        # Definir el numero de turno
        numero = Turno.query.count() + 1
        # Crear el nuevo turno
        turno = Turno(
            usuario=usuario,
            turno_estado=turno_estado,
            turno_tipo=turno_tipo,
            ventanilla=ventanilla,
            numero=numero,
            unidad_id=unidad.id,
            comentarios=safe_string(turno_in.comentarios),
        )
        turno.save()
        # Entregar JSON
        return OneTurnoSchemaOut(
            success=True,
            message=f"Se ha creado el turno {turno.numero} por el usuario {username}",
            data=TurnoSchemaOut(
                id=turno.id,
                numero=turno.numero,
                comentarios=turno.comentarios,
            ),
        ).model_dump()
