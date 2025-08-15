"""
API-Key v1 Endpoint: Crear Turno
"""

from datetime import datetime

from flask import current_app, request, url_for
from flask_restful import Resource
from pytz import timezone
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from lib.safe_string import safe_string, safe_message
from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import OneTurnoOut, UnidadOut, TurnoOut, VentanillaOut
from tauro.blueprints.api_key_v1.schemas import CrearTurnoIn
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.ventanillas.models import Ventanilla
from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo

from tauro.extensions import socketio


class CrearTurno(Resource):
    """Crear un nuevo turno"""

    @api_key_required
    def post(self) -> OneTurnoOut:
        """Crear un turno"""

        # Recibir y validar el payload
        payload = request.get_json()
        crear_turno_in = CrearTurnoIn.model_validate(payload)

        # Consultar el usuario
        try:
            usuario = Usuario.query.filter_by(id=crear_turno_in.usuario_id).filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()

        # Consultar el tipo de turno
        turno_tipo = TurnoTipo.query.get(crear_turno_in.turno_tipo_id)
        if turno_tipo is None:
            return OneTurnoOut(
                success=False,
                message="Tipo de turno no encontrado",
            ).model_dump()

        # Consultar la unidad
        unidad = Unidad.query.get(crear_turno_in.unidad_id)
        if unidad is None:
            return OneTurnoOut(
                success=False,
                message="Unidad no encontrada",
            ).model_dump()

        # Consultar el estado de turno "EN ESPERA"
        try:
            turno_estado = TurnoEstado.query.filter_by(nombre="EN ESPERA").filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoOut(
                success=False,
                message="Estado de turno no encontrado",
            ).model_dump()

        # Consultar la ventanilla NO DEFINIDO
        try:
            ventanilla = Ventanilla.query.filter_by(nombre="NO DEFINIDO").filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoOut(
                success=False,
                message="Ventanilla no encontrada",
            ).model_dump()

        # Definir el numero de turno
        fecha_hoy = datetime.now(tz=timezone(current_app.config["TZ"])).date()
        timestamp_hoy = datetime(year=fecha_hoy.year, month=fecha_hoy.month, day=fecha_hoy.day, hour=0, minute=0, second=0)
        numero = Turno.query.filter(Turno.creado >= timestamp_hoy).count() + 1

        # Crear el nuevo turno
        turno = Turno(
            usuario=usuario,
            turno_estado=turno_estado,
            turno_tipo=turno_tipo,
            ventanilla=ventanilla,
            numero=numero,
            unidad_id=unidad.id,
            comentarios=safe_string(crear_turno_in.comentarios),
        )
        turno.save()

        # Crear registro en bitácora
        Bitacora(
            modulo=Modulo.query.filter_by(nombre="TURNOS").first(),
            usuario=usuario,
            descripcion=safe_message(f"El turno {turno.id} ha sido creado por Api-Key"),
            url=url_for("turnos.detail", turno_id=turno.id),
        ).save()

        # Extraer la unidad
        unidad_out = None
        if unidad is not None:
            unidad_out = UnidadOut(
                id=unidad.id,
                clave=unidad.clave,
                nombre=unidad.nombre,
            )

        # Crear nuevo objeto OneTurnoOut
        turno_out = OneTurnoOut(
            success=True,
            message=f"Se ha creado el turno {turno.numero} en {unidad.clave} por {usuario.nombre}",
            data=TurnoOut(
                turno_id=turno.id,
                turno_numero=turno.numero,
                turno_fecha=turno.creado.isoformat(),
                turno_estado=turno.turno_estado.nombre,
                turno_tipo_id=turno.turno_tipo_id,
                turno_comentarios=turno.comentarios,
                ventanilla=VentanillaOut(
                    id=turno.ventanilla.id,
                    nombre=turno.ventanilla.nombre,
                    numero=turno.ventanilla.numero,
                ),
                unidad=unidad_out,
            ),
        ).model_dump()

        # Ejecutar send socket-io. Envía una variable "message" con la estructura json
        socketio.send(turno_out)

        # Entregar JSON
        return turno_out
