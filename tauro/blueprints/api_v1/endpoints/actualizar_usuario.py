"""
API v1 Endpoint: Actualizar Usuario
"""

from flask import g, request
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import (
    ActualizarUsuarioIn,
    OneVentanillaUsuarioOut,
    TurnoOut,
    TurnoTipoOut,
    VentanillaUsuarioOut,
)
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo
from tauro.blueprints.ventanillas.models import Ventanilla


class ActualizarUsuario(Resource):
    """Actualizar un usuario"""

    @token_required
    def post(self) -> OneVentanillaUsuarioOut:
        """Actualizar un usuario"""

        # Consultar el usuario
        username = g.current_user
        try:
            usuario = Usuario.query.filter_by(email=username).filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneVentanillaUsuarioOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()

        # Recibir y validar el payload
        payload = request.get_json()
        actualizar_usuario_in = ActualizarUsuarioIn.model_validate(payload)

        # Actualizar TODOS los tipos de turnos que el usuario ESTA atendiendo con es_activo a falso
        for usuario_turno_tipo in UsuarioTurnoTipo.query.filter_by(usuario_id=usuario.id).all():
            if usuario_turno_tipo.es_activo:
                usuario_turno_tipo.es_activo = False
                usuario_turno_tipo.save()

        # Consultar los tipos de turnos que el usuario QUIERE atender
        turnos_tipos = (
            TurnoTipo.query.filter(TurnoTipo.id.in_(actualizar_usuario_in.turnos_tipos_ids))
            .filter(TurnoTipo.es_activo == True)
            .filter(TurnoTipo.estatus == "A")
            .all()
        )

        # Agregar o actualizar en la tabla usuarios_turnos_tipos
        for turno_tipo in turnos_tipos:
            # ¿Estará en la tabla?
            usuario_turno_tipo = (
                UsuarioTurnoTipo.query.filter_by(usuario_id=usuario.id)
                .filter_by(turno_tipo_id=turno_tipo.id)
                .filter_by(estatus="A")
                .first()
            )
            # Si NO esta, lo agregamos
            if usuario_turno_tipo is None:
                nuevo_utt = UsuarioTurnoTipo(
                    usuario_id=usuario.id,
                    turno_tipo_id=turno_tipo.id,
                    es_activo=True,
                )
                nuevo_utt.save()
            else:
                # Si ya estaba y es_activo es falso, lo actualizamos a verdadero
                if usuario_turno_tipo.es_activo is False:
                    usuario_turno_tipo.es_activo = True
                    usuario_turno_tipo.save()

        # Consultar la ventanilla
        ventanilla = Ventanilla.query.get(actualizar_usuario_in.ventanilla_id)
        if ventanilla is None:
            return OneVentanillaUsuarioOut(
                success=False,
                message="Ventanilla no encontrada",
            ).model_dump()
        if ventanilla.estatus != "A":
            return OneVentanillaUsuarioOut(
                success=False,
                message="Ventanilla eliminada",
            ).model_dump()
        if ventanilla.es_activo is False:
            return OneVentanillaUsuarioOut(
                success=False,
                message="Ventanilla no activa",
            ).model_dump()

        # Consultar los usuarios por la ventanilla, si la ventanilla la tiene otro usuario, se le manda un error
        usuarios = Usuario.query.filter_by(ventanilla_id=ventanilla.id).filter_by(estatus="A").first()
        if usuarios is not None and usuarios.id != usuario.id:
            return OneVentanillaUsuarioOut(
                success=False,
                message="Ventanilla ocupada por otro usuario",
            ).model_dump()

        # Actualizar la ventanilla del usuario
        usuario.ventanilla_id = ventanilla.id

        # Guardar
        usuario.save()

        # Consultar el último turno en "EN ESPERA" o "ATENDIENDO" del usuario
        turnos = (
            Turno.query.join(TurnoEstado)
            .filter(or_(TurnoEstado.nombre == "EN ESPERA", TurnoEstado.nombre == "ATENDIENDO"))
            .filter(Turno.usuario_id == usuario.id)
            .order_by(Turno.id.desc())
            .first()
        )
        ultimo_turno = None
        if turnos:
            ultimo_turno = TurnoOut(id=turnos.id, numero=turnos.numero, comentarios=turnos.comentarios)

        # Entregar JSON
        return OneVentanillaUsuarioOut(
            success=True,
            message="Usuario actualizado",
            data=VentanillaUsuarioOut(
                id=usuario.ventanilla_id,
                ventanilla=ventanilla.nombre,
                turnos_tipos=[TurnoTipoOut(id=tt.id, nombre=tt.nombre) for tt in turnos_tipos],
                usuario_nombre_completo=usuario.nombre,
                ultimo_turno=ultimo_turno,
            ),
        ).model_dump()
