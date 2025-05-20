"""
API v1 Endpoint: Consultar Configuracion Usuario
"""

from flask import g
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import (
    OneVentanillaUsuarioOut,
    TurnoOut,
    TurnoTipoOut,
    VentanillaUsuarioOut,
    VentanillaActivaOut,
    VentanillaOut,
    UnidadOut,
    RolOut,
)
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo
from tauro.blueprints.ventanillas.models import Ventanilla
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.usuarios_roles.models import UsuarioRol


class ConsultarConfiguracionUsuario(Resource):
    """Consultar configuración del usuario"""

    @token_required
    def get(self) -> OneVentanillaUsuarioOut:
        """Consultar configuración del usuario"""

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
            turnos_tipos = [
                TurnoTipoOut(id=utt.turno_tipo.id, nombre=utt.turno_tipo.nombre, nivel=utt.turno_tipo.nivel)
                for utt in usuarios_turnos_tipos
            ]

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
            ultimo_turno = TurnoOut(
                turno_id=turnos.id,
                turno_numero=turnos.numero,
                turno_estado=turnos.turno_estado.nombre,
                turno_comentarios=turnos.comentarios,
                ventanilla=VentanillaOut(
                    id=turnos.ventanilla.id,
                    nombre=turnos.ventanilla.nombre,
                    numero=turnos.ventanilla.numero,
                ),
            )
        # Consultar la ventanilla del usuario
        ventanilla_sql = Ventanilla.query.get(usuario.ventanilla_id)
        ventanilla = VentanillaOut(id=ventanilla_sql.id, nombre=ventanilla_sql.nombre, numero=ventanilla_sql.numero)
        # Extraer un único rol
        usuarios_roles = UsuarioRol.query.filter_by(usuario_id=usuario.id).filter_by(estatus="A").first()
        if usuarios_roles is None:
            return OneVentanillaUsuarioOut(
                success=False,
                message="El usuario no tiene un rol asignado",
            ).model_dump
        rol = usuarios_roles.rol
        # Consultar la unidad
        unidad_sql = Unidad.query.get(usuario.unidad_id)
        if unidad_sql:
            unidad = UnidadOut(
                id=unidad_sql.id,
                clave=unidad_sql.clave,
                nombre=unidad_sql.nombre,
            )

        # Entregar JSON
        return OneVentanillaUsuarioOut(
            success=True,
            message=f"Se ha consultado la ventanilla de {username}",
            data=VentanillaUsuarioOut(
                ventanilla=ventanilla,
                unidad=unidad,
                turnos_tipos=turnos_tipos,
                usuario_nombre_completo=usuario.nombre,
                rol=RolOut(
                    id=rol.id,
                    nombre=rol.nombre,
                ),
                ultimo_turno=ultimo_turno,
            ),
        ).model_dump()
