"""
API-OAuth2 v1 Endpoint: Actualizar Usuario
"""

from flask import g, request, url_for
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from lib.safe_string import safe_message

from tauro.blueprints.api_oauth2_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import (
    TurnoTipoOut,
    TurnoOut,
    VentanillaOut,
    UnidadOut,
    RolOut,
    ConfiguracionUsuarioOut,
    OneConfiguracionUsuarioOut,
)
from tauro.blueprints.api_oauth2_v1.schemas import ActualizarUsuarioIn
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo
from tauro.blueprints.ventanillas.models import Ventanilla
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.usuarios_roles.models import UsuarioRol
from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo


class ActualizarUsuario(Resource):
    """Actualizar un usuario"""

    @token_required
    def post(self) -> OneConfiguracionUsuarioOut:
        """Actualizar un usuario"""

        # Consultar el usuario
        username = g.current_user
        try:
            usuario = Usuario.query.filter_by(email=username).filter_by(estatus="A").one()
        except (MultipleResultsFound, NoResultFound):
            return OneConfiguracionUsuarioOut(
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
            return OneConfiguracionUsuarioOut(
                success=False,
                message="Ventanilla no encontrada",
            ).model_dump()
        if ventanilla.estatus != "A":
            return OneConfiguracionUsuarioOut(
                success=False,
                message="Ventanilla eliminada",
            ).model_dump()
        if ventanilla.es_activo is False:
            return OneConfiguracionUsuarioOut(
                success=False,
                message="Ventanilla no activa",
            ).model_dump()

        # Consultar los usuarios por la ventanilla, si la ventanilla la tiene otro usuario, se le manda un error
        usuarios = Usuario.query.filter_by(ventanilla_id=ventanilla.id).filter_by(estatus="A").first()
        if usuarios is not None and usuarios.id != usuario.id:
            return OneConfiguracionUsuarioOut(
                success=False,
                message=f"Ventanilla ocupada por {usuarios.nombre}",
            ).model_dump()

        # Actualizar la ventanilla del usuario
        usuario.ventanilla_id = ventanilla.id

        # Guardar
        usuario.save()

        # Crear registro en bitácora
        Bitacora(
            modulo=Modulo.query.filter_by(nombre="USUARIOS").first(),
            usuario=usuario,
            descripcion=safe_message(f"El usuario ha sido actualizado por Api-OAuth2"),
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        ).save()

        # Consultar Ventanilla
        ventanilla = None
        ventanilla_sql = Ventanilla.query.get(usuario.ventanilla_id)
        if ventanilla_sql:
            ventanilla = VentanillaOut(
                id=ventanilla_sql.id,
                nombre=ventanilla_sql.nombre,
                numero=ventanilla_sql.numero,
            )

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
            # Consultar la unidad
            unidad = Unidad.query.get(turnos.unidad_id)
            # Extraer la unidad
            unidad_out = None
            if unidad:
                unidad_out = UnidadOut(
                    id=unidad.id,
                    clave=unidad.clave,
                    nombre=unidad.nombre,
                )
            ultimo_turno = TurnoOut(
                turno_id=turnos.id,
                turno_numero=turnos.numero,
                turno_fecha=turnos.creado.isoformat(),
                turno_estado=turnos.turno_estado.nombre,
                turno_tipo_id=turnos.turno_tipo_id,
                turno_numero_cubiculo=turnos.numero_cubiculo,
                turno_comentarios=turnos.comentarios,
                ventanilla=VentanillaOut(
                    id=turnos.ventanilla.id,
                    nombre=turnos.ventanilla.nombre,
                    numero=turnos.ventanilla.numero,
                ),
                unidad=unidad_out,
            )

        # # Extraer un único rol
        usuarios_roles = UsuarioRol.query.filter_by(usuario_id=usuario.id).filter_by(estatus="A").first()
        if usuarios_roles is None:
            return OneConfiguracionUsuarioOut(
                success=False,
                message="El usuario no tiene un rol asignado",
            ).model_dump()
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
        return OneConfiguracionUsuarioOut(
            success=True,
            message="Usuario actualizado",
            data=ConfiguracionUsuarioOut(
                ventanilla=ventanilla,
                unidad=unidad,
                rol=RolOut(
                    id=rol.id,
                    nombre=rol.nombre,
                ),
                turnos_tipos=[TurnoTipoOut(id=tt.id, nombre=tt.nombre, nivel=tt.nivel) for tt in turnos_tipos],
                usuario_nombre_completo=usuario.nombre,
                ultimo_turno=ultimo_turno,
            ),
        ).model_dump()
