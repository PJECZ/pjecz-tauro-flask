"""
API v1 Endpoint: Actualizar Usuario
"""

from flask import g, request
from flask_restful import Resource
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import ActualizarUsuarioSchemaIn, OneVentanillaUsuarioSchemaOut
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo


class ActualizarUsuario(Resource):
    """Actualizar un usuario"""

    @token_required
    def post(self) -> OneVentanillaUsuarioSchemaOut:
        """Actualizar un usuario"""
        # Consultar el usuario
        username = g.current_user
        try:
            usuario = Usuario.query.filter_by(email=username).one()
        except (MultipleResultsFound, NoResultFound):
            return OneVentanillaUsuarioSchemaOut(
                success=False,
                message="Usuario no encontrado",
            ).model_dump()
        # Recibir y validar ActualizarUsuarioSchemaIn
        payload = request.get_json()
        actualizar_usuario_in = ActualizarUsuarioSchemaIn.model_validate(payload)
        # Actualizar los tipos de turnos que el usuario ESTA atendiendo con es_activo a falso
        for usuario_turno_tipo in UsuarioTurnoTipo.query.filter_by(usuario_id=usuario.id).all():
            usuario_turno_tipo.es_activo = False
            usuario_turno_tipo.save()
        # Consultar los tipos de turnos que el usuario QUIERE atender
        turnos_tipos = TurnoTipo.query.filter(TurnoTipo.nombre.in_(actualizar_usuario_in.turnos_tipos_nombres)).all()
        for turno_tipo in turnos_tipos:
            # ¿Estará en la tabla?
            usuarios_turnos_tipos = (
                UsuarioTurnoTipo.query.filter_by(usuario_id=usuario.id).filter(turnos_tipos_id=turnos_tipos.id).first()
            )
            # Si NO esta, lo agregamos
            if usuarios_turnos_tipos is None:
                nuevo_utt = UsuarioTurnoTipo(
                    usuario_id=usuario.id,
                    turno_tipo_id=turno_tipo.id,
                    es_activo=True,
                )
                nuevo_utt.save()
            else:
                # Si ya estaba, lo actualizamos con es_activo a verdadero
                usuarios_turnos_tipos.es_activo = True
                usuarios_turnos_tipos.save()
        # Actualizar el usuario
        usuario.ventana_id = actualizar_usuario_in.ventanilla_id
        # Guardar cambios
        usuario.save()
