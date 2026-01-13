"""
API-Key v1 Endpoint: Tomar Turno
"""

from datetime import datetime
from flask import request, url_for
from flask_restful import Resource
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from lib.safe_string import safe_message

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import OneTurnoOut, TurnoOut, UbicacionOut, UnidadOut
from tauro.blueprints.api_key_v1.schemas import ConsultarUsuarioIn
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo

from tauro.extensions import socketio


class TomarTurno(Resource):
    """Tomar un turno"""

    @api_key_required
    def post(self) -> OneTurnoOut:
        """Tomar un turno"""

        # Recibir y validar el payload
        payload = request.get_json()
        usuario_in = ConsultarUsuarioIn.model_validate(payload)

        # Consultar el usuario
        try:
            usuario = Usuario.query.filter_by(id=usuario_in.usuario_id).filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()

        # Consultar los tipos de turnos del usuario
        usuarios_turnos_tipos = (
            UsuarioTurnoTipo.query.filter_by(usuario_id=usuario.id).filter_by(es_activo=True).filter_by(estatus="A").all()
        )
        if usuarios_turnos_tipos is None:
            return OneTurnoOut(
                success=False,
                message="No ha elegido los tipos de turnos que atenderá",
            ).model_dump()
        tipos_turnos = [utt.turno_tipo.nombre for utt in usuarios_turnos_tipos]

        # Tomar un turno...
        # - Filtrar el estado del turno "EN ESPERA",
        # - Filtrar los tipos de turnos que tiene el usuario, por ejemplo ["ATENCION URGENTE", "NORMAL"]
        # - Filtrar la unidad del usuario,
        # - Ordenar por el nombre del tipo de turno, luego por el número del turno
        # - Tomar solo el primero
        turno = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(TurnoEstado.nombre == "EN ESPERA")
            .filter(TurnoTipo.nombre.in_(tipos_turnos))
            .filter(Turno.unidad_id == usuario.unidad_id)
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nombre, Turno.numero)
            .first()
        )

        # Si no hay turnos en espera, retornar error
        if turno is None:
            return OneTurnoOut(
                success=False,
                message="No hay turnos en espera",
            ).model_dump()

        # Consultar el estado de turno "ATENDIENDO"
        try:
            turno_estado = TurnoEstado.query.filter_by(nombre="ATENDIENDO").one()
        except (MultipleResultsFound, NoResultFound):
            return OneTurnoOut(
                success=False,
                message="Estado de turno no encontrado",
            ).model_dump()

        # Cambiar el usuario, el estado a "ATENDIENDO" y la ubicacion, así como el tiempo de inicio
        turno.usuario_id = usuario.id
        turno.turno_estado_id = turno_estado.id
        turno.ubicacion_id = usuario.ubicacion_id
        turno.inicio = datetime.now()

        # Guardar
        turno.save()

        # Crear registro en bitácora
        Bitacora(
            modulo=Modulo.query.filter_by(nombre="TURNOS").first(),
            usuario=usuario,
            descripcion=safe_message(f"El turno {turno.id} ha sido tomado utilizando Api-Key"),
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
            message=f"Turno {turno.numero} tomado por {usuario.nombre}",
            data=TurnoOut(
                turno_id=turno.id,
                turno_numero=turno.numero,
                turno_fecha=turno.creado.isoformat(),
                turno_estado=turno.turno_estado.nombre,
                turno_tipo_id=turno.turno_tipo_id,
                turno_numero_cubiculo=turno.numero_cubiculo,
                turno_telefono=turno.telefono,
                turno_comentarios=turno.comentarios,
                ubicacion=UbicacionOut(
                    id=turno.ubicacion.id,
                    nombre=turno.ubicacion.nombre,
                    numero=turno.ubicacion.numero,
                ),
                unidad=unidad_out,
            ),
        ).model_dump()

        # Enviar mensaje socketio
        socketio.send(one_turno_out)

        # Entregar JSON
        return one_turno_out
