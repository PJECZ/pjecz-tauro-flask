"""
API v1 Endpoint: Actualizar Turno Estado
"""

from datetime import datetime

from flask import g, request
from flask_restful import Resource
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import ActualizarTurnoEstadoIn, OneTurnoOut, TurnoOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.usuarios.models import Usuario


class ActualizarTurnoEstado(Resource):
    """Actualizar el estado de un turno"""

    @token_required
    def post(self) -> OneTurnoOut:
        """Actualizar el estado de un turno"""

        # Consultar el usuario
        username = g.current_user
        try:
            usuario = Usuario.query.filter_by(email=username).filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()

        # Recibir y validar el payload
        payload = request.get_json()
        turno_estado_in = ActualizarTurnoEstadoIn.model_validate(payload)

        # Consultar el turno
        turno = Turno.query.get(turno_estado_in.id)
        if turno is None:
            return OneTurnoOut(
                success=False,
                message="Turno no encontrado",
            ).model_dump()

        # Si el estado que tiene el turno es el mismo que se quiere asignar, no hacer nada
        if turno.turno_estado_id == turno_estado_in.turno_estado_id:
            return OneTurnoOut(
                success=False,
                message="El estado del turno ya ha sido cambiado como se desea",
            ).model_dump()

        # Consultar el NUEVO estado de turno
        turno_estado = TurnoEstado.query.get(turno_estado_in.turno_estado_id)
        if turno_estado is None:
            return OneTurnoOut(
                success=False,
                message="Estado de turno no encontrado",
            ).model_dump()

        # Cambiar el estado del turno
        turno.turno_estado_id = turno_estado.id

        # Si el estado es "COMPLETADO", definir el tiempo de término
        if turno_estado.nombre == "COMPLETADO":
            turno.termino = datetime.now()

        # Guardar cambios
        turno.save()

        # Entregar JSON
        return OneTurnoOut(
            success=True,
            message=f"Se ha cambiado el turno {turno.numero} a {turno_estado.nombre} por {username}",
            data=TurnoOut(
                id=turno.id,
                numero=turno.numero,
                comentarios=turno.comentarios,
            ),
        ).model_dump()
