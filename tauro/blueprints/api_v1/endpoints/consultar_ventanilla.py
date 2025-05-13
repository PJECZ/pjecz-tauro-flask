"""
API v1 Endpoint: Consultar Ventanilla
"""

from flask import g
from flask_restful import Resource
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import OneVentanillaUsuarioSchemaOut, TurnoSchemaOut, VentanillaUsuarioSchemaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo


class ConsultarVentanilla(Resource):
    """Consultar ventanilla del usuario"""

    @token_required
    def get(self) -> OneVentanillaUsuarioSchemaOut:
        """Consultar ventanilla del usuario"""
        username = g.current_user
        # Consultar el usuario
        try:
            usuario = Usuario.query.filter_by(email=username).one()
        except (MultipleResultsFound, NoResultFound):
            return OneVentanillaUsuarioSchemaOut(
                success=False,
                message="Usuario no encontrado o email duplicado",
            ).model_dump()
        # Consultar los tipos de turnos del usuario
        usuarios_turnos_tipos = UsuarioTurnoTipo.query.filter_by(usuario_id=usuario.id).filter_by(es_activo=True).all()
        # Consultar el último turno en "EN ESPERA" del usuario
        turnos = (
            Turno.query.join(TurnoEstado)
            .filter(TurnoEstado.nombre == "EN ESPERA")
            .filter(Turno.usuario_id == usuario.id)
            .order_by(Turno.id.desc())
            .first()
        )
        # Preparar el data
        data = VentanillaUsuarioSchemaOut(
            nombre=usuario.ventanilla.nombre,
            turnos_tipos_nombres=[utt.nombre for utt in usuarios_turnos_tipos] if usuarios_turnos_tipos else None,
            usuario_nombre_completo=usuario.nombre,
            ultimo_turno=TurnoSchemaOut(id=turnos.id, numero=turnos.numero, comentarios=turnos.comentarios) if turnos else None,
        )
        # Entregar JSON
        return OneVentanillaUsuarioSchemaOut(
            success=True,
            message=f"Se ha consultado la ventanilla de {username}",
            data=data,
        ).model_dump()
