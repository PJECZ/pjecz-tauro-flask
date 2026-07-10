"""
API-Key v1 Endpoint: Consultar Configuración Usuario
"""

from flask import request
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from tauro.blueprints.api_key_v1.endpoints.autenticar import api_key_required
from tauro.blueprints.api_v1.schemas import (
    RolOut,
    UnidadOut,
    TurnoTipoOut,
    TurnoEstadoOut,
    TurnoOut,
    UbicacionOut,
    OneConfiguracionUsuarioOut,
    ConfiguracionUsuarioOut,
)
from tauro.blueprints.api_key_v1.schemas import ConsultarUsuarioIn
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo
from tauro.blueprints.ubicaciones.models import Ubicacion
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.usuarios_roles.models import UsuarioRol


class ConsultarConfiguracionUsuario(Resource):
    """Consultar configuración del usuario"""

    @api_key_required
    def post(self) -> OneConfiguracionUsuarioOut:
        """Consultar configuración del usuario"""

        # Recibir y validar el payload
        payload = request.get_json()
        usuario_in = ConsultarUsuarioIn.model_validate(payload)

        # Consultar el usuario
        try:
            usuario = Usuario.query.filter_by(id=usuario_in.usuario_id).filter_by(estatus="A").one()
        except MultipleResultsFound, NoResultFound:
            return OneConfiguracionUsuarioOut(
                success=False,
                message="Usuario no encontrado",
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

        # Consultar el último turno del usuario
        turno = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(
                or_(
                    TurnoEstado.nombre == "ATENDIENDO",
                    TurnoEstado.nombre == "ATENDIENDO EN CUBICULO",
                    TurnoEstado.nombre == "PASE A UBICACION",
                    TurnoEstado.nombre == "PASE A CUBICULO",
                )
            )
            .filter(Turno.estatus == "A")
            .filter(Turno.usuario_id == usuario.id)
            .order_by(TurnoTipo.nivel, Turno.numero)
            .first()
        )
        ultimo_turno = None

        if turno:
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

            ultimo_turno = TurnoOut(
                turno_id=turno.id,
                turno_numero=turno.numero,
                turno_fecha=turno.creado.isoformat(),
                turno_numero_cubiculo=turno.numero_cubiculo,
                turno_telefono=turno.telefono,
                turno_comentarios=turno.comentarios,
                turno_estado=TurnoEstadoOut(
                    id=turno.turno_estado.id,
                    nombre=turno.turno_estado.nombre,
                ),
                turno_tipo=TurnoTipoOut(
                    id=turno.turno_tipo.id,
                    nombre=turno.turno_tipo.nombre,
                    nivel=turno.turno_tipo.nivel,
                ),
                ubicacion=UbicacionOut(
                    id=turno.ubicacion.id,
                    nombre=turno.ubicacion.nombre,
                    numero=turno.ubicacion.numero,
                ),
                unidad=unidad_out,
            )
        # Consultar la ubicación del usuario
        ubicacion_sql = Ubicacion.query.get(usuario.ubicacion_id)
        ubicacion = UbicacionOut(id=ubicacion_sql.id, nombre=ubicacion_sql.nombre, numero=ubicacion_sql.numero)
        # Extraer un único rol
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
            message=f"Se ha consultado la configuración del usuario {usuario.nombre}",
            data=ConfiguracionUsuarioOut(
                usuario_nombre_completo=usuario.nombre,
                ubicacion=ubicacion,
                unidad=unidad,
                turnos_tipos=turnos_tipos,
                rol=RolOut(
                    id=rol.id,
                    nombre=rol.nombre,
                ),
                ultimo_turno=ultimo_turno,
            ),
        ).model_dump()
