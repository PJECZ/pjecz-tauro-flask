"""
API-Key v1 Endpoint: Actualizar Turno Estado
"""

from datetime import datetime

from flask import request, url_for
from flask_restful import Resource
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import UnidadOut, TurnoOut, VentanillaOut, OneTurnoOut
from tauro.blueprints.api_key_v1.schemas import ActualizarTurnoEstadoIn
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo

from lib.safe_string import safe_message
from tauro.extensions import socketio


class ActualizarTurnoEstado(Resource):
    """Actualizar el estado de un turno"""

    @api_key_required
    def post(self) -> OneTurnoOut:
        """Actualizar el estado de un turno"""

        # Recibir y validar el payload
        payload = request.get_json()
        actualizar_turno_estado_in = ActualizarTurnoEstadoIn.model_validate(payload)

        # Consultar el usuario
        try:
            usuario = Usuario.query.filter_by(id=actualizar_turno_estado_in.usuario_id).filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()

        # Consultar el turno
        turno = Turno.query.get(actualizar_turno_estado_in.turno_id)
        if turno is None:
            return OneTurnoOut(
                success=False,
                message="Turno no encontrado",
            ).model_dump()

        # Si el estado que tiene el turno es el mismo que se quiere asignar, no hacer nada
        if turno.turno_estado_id == actualizar_turno_estado_in.turno_estado_id:
            return OneTurnoOut(
                success=False,
                message="El estado del turno ya ha sido cambiado como se desea",
            ).model_dump()

        # Consultar el NUEVO estado de turno
        turno_estado = TurnoEstado.query.get(actualizar_turno_estado_in.turno_estado_id)
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
        # Si el estado es "ATENDIENDO", definir el tiempo de inicio
        if turno_estado.nombre == "ATENDIENDO":
            turno.inicio = datetime.now()

        # Guardar cambios
        turno.save()

        # Crear registro en bitácora
        Bitacora(
            modulo=Modulo.query.filter_by(nombre="TURNOS").first(),
            usuario=usuario,
            descripcion=safe_message(f"El turno {turno.id} ha sido cambiado a {turno_estado.nombre} por Api-Key"),
            url=url_for("turnos.detail", turno_id=turno.id),
        ).save()

        # Consultar la unidad
        unidad = Unidad.query.get(turno.unidad_id)
        # Extraer la unidad
        unidad_out = None
        if unidad is not None:
            unidad_out = UnidadOut(
                id=unidad.id,
                clave=unidad.clave,
                nombre=unidad.nombre,
            )

        # Crear objeto OneTurnoOut
        one_turno_out = OneTurnoOut(
            success=True,
            message=f"Se ha cambiado el turno {turno.numero} a {turno_estado.nombre} por {usuario.nombre}",
            data=TurnoOut(
                turno_id=turno.id,
                turno_numero=turno.numero,
                turno_estado=turno.turno_estado.nombre,
                turno_comentarios=turno.comentarios,
                ventanilla=VentanillaOut(
                    id=turno.ventanilla.id,
                    nombre=turno.ventanilla.nombre,
                    numero=turno.ventanilla.numero,
                ),
                unidad=unidad_out,
            ),
        ).model_dump()

        # Enviar mensaje vía socketio
        socketio.send(one_turno_out)

        # Entregar JSON
        return one_turno_out
