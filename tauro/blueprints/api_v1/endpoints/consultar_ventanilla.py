"""
API v1 Endpoint: Consultar Ventanilla
"""

from flask import g
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import OneVentanillaUsuarioOut, TurnoOut, TurnoTipoOut, VentanillaUsuarioOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo


class ConsultarVentanilla(Resource):
    """Consultar ventanilla del usuario"""

    @token_required
    def get(self) -> OneVentanillaUsuarioOut:
        """Consultar ventanilla del usuario"""

        # Consultar el usuario
        username = g.current_user
        try:
            usuario = Usuario.query.filter_by(email=username).filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneVentanillaUsuarioOut(
                success=False,
                message="Usuario no encontrado o email duplicado",
            ).model_dump()

        # Consultar los tipos de turnos del usuario
        usuarios_turnos_tipos = (
            UsuarioTurnoTipo.query.filter_by(usuario_id=usuario.id).filter_by(es_activo=True).filter_by(estatus="A").all()
        )
        turnos_tipos = None
        if usuarios_turnos_tipos:
            turnos_tipos = [TurnoTipoOut(id=utt.turno_tipo.id, nombre=utt.turno_tipo.nombre) for utt in usuarios_turnos_tipos]

        # Consultar el último turno en "EN ESPERA" o "ATENDIENDO" del usuario
        turnos = (
            Turno.query.join(TurnoEstado)
            .filter(or_(TurnoEstado.nombre == "EN ESPERA", TurnoEstado.nombre == "ATENDIENDO"))
            .filter(Turno.usuario_id == usuario.id)
            .filter(Turno.estatus == "A")
            .order_by(Turno.id.desc())
            .first()
        )
        ultimo_turno = None
        if turnos:
            ultimo_turno = TurnoOut(id=turnos.id, numero=turnos.numero, comentarios=turnos.comentarios)

        # Entregar JSON
        return OneVentanillaUsuarioOut(
            success=True,
            message=f"Se ha consultado la ventanilla de {username}",
            data=VentanillaUsuarioOut(
                id=usuario.ventanilla.id,
                ventanilla=usuario.ventanilla.nombre,
                turnos_tipos=turnos_tipos,
                usuario_nombre_completo=usuario.nombre,
                ultimo_turno=ultimo_turno,
            ),
        ).model_dump()
