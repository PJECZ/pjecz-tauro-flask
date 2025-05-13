"""
API v1 Endpoint: Cambiar Turno Estado
"""

from flask import g, request
from flask_restful import Resource
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import OneTurnoSchemaOut, TurnoEstadoIn, TurnoSchemaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.usuarios.models import Usuario


class CambiarTurnoEstado(Resource):
    """Cambiar el estado de un turno"""

    @token_required
    def post(self) -> OneTurnoSchemaOut:
        """Cambiar el estado de un turno"""
        # Consultar el usuario
        username = g.current_user
        try:
            usuario = Usuario.query.filter_by(email=username).one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoSchemaOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()
        # Recibir y validar TurnoEstadoIn
        payload = request.get_json()
        turno_estado_in = TurnoEstadoIn.model_validate(payload)
        # Consultar el turno
        turno = Turno.query.get(turno_estado_in.turno_id)
        if turno is None:
            return OneTurnoSchemaOut(
                success=False,
                message="Turno no encontrado",
            ).model_dump()
        # Consultar el estado de turno
        try:
            turno_estado = TurnoEstado.query.filter_by(nombre=turno_estado_in.turno_estado_nombre).one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoSchemaOut(
                success=False,
                message="Estado de turno no encontrado",
            ).model_dump()
        # Si el estado que tiene el turno es el mismo que se quiere asignar, no hacer nada
        if turno.turno_estado_id == turno_estado.id:
            return OneTurnoSchemaOut(
                success=False,
                message=f"El estado del turno ya es {turno_estado_in.turno_estado_nombre}",
            ).model_dump()
        # Cambiar el estado del turno
        turno.turno_estado_id = turno_estado.id
        # Guardar cambios
        turno.save()
        # Entregar JSON
        return OneTurnoSchemaOut(
            success=True,
            message=f"Se ha cambiado el estado del turno a {turno_estado_in.turno_estado_nombre}",
            data=TurnoSchemaOut(
                id=turno.id,
                numero=turno.numero,
                comentarios=turno.comentarios,
            ),
        ).model_dump()
