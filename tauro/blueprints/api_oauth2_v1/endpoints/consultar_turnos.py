"""
API v1 Endpoint: Consultar Turnos
"""

from flask import current_app
from flask_restful import Resource
from sqlalchemy import or_

from tauro.blueprints.api_oauth2_v1.schemas import (
    ListTurnosOut,
    OneListTurnosOut,
    TurnoUnidadOut,
    UnidadOut,
    UbicacionOut,
    TurnoEstadoOut,
    TurnoTipoOut,
)
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnos(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO"""

    def get(self) -> OneListTurnosOut:
        """Consultar los turnos EN ESPERA y ATENDIENDO, aquí NO SE USA el decorador porque es para pantallas"""

        # Consultar los turnos...
        # - Filtrar por los estados EN ESPERA y ATENDIENDO,
        # - Filtrar por el estatus A (activo),
        # - Y ordenar por el nombre de tipo de turno ATENCION URGENTE, CON CITA, NORMAL y luego por el número
        turnos = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(TurnoEstado.nombre != "COMPLETADO", TurnoEstado.nombre != "CANCELADO")
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .limit(current_app.config["LIMITE_DE_TURNOS_LISTADOS"])
            .all()
        )

        # Si no se encuentran turnos, entregar success en verdadero
        if not turnos:
            return OneListTurnosOut(
                success=True,
                message="No hay turnos en espera",
            ).model_dump()

        # Consultar Unidades
        unidades_sql = Unidad.query.all()
        unidades = {unidad.id: unidad for unidad in unidades_sql}

        # Consultar Estados
        estados_sql = TurnoEstado.query.all()
        estados = {estado.id: estado for estado in estados_sql}

        # Consultar Tipos
        tipos_sql = TurnoTipo.query.all()
        tipos = {tipo.id: tipo for tipo in tipos_sql}

        # Consultar Último turno en estado 'ATENDIENDO' o 'ATENDIENDO EN CUBÍCULO'
        ultimo_turno_atendiendo = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(or_(TurnoEstado.nombre == "ATENDIENDO", TurnoEstado.nombre == "ATENDIENDO EN CUBICULO"))
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .first()
        )
        if ultimo_turno_atendiendo:
            ultimo_turno = TurnoUnidadOut(
                turno_id=ultimo_turno_atendiendo.id,
                turno_numero=ultimo_turno_atendiendo.numero,
                turno_fecha=ultimo_turno_atendiendo.creado.isoformat(),
                turno_numero_cubiculo=ultimo_turno_atendiendo.numero_cubiculo,
                turno_telefono=ultimo_turno_atendiendo.telefono,
                turno_comentarios=ultimo_turno_atendiendo.comentarios,
                turno_estado=TurnoEstadoOut(
                    id=estados[ultimo_turno_atendiendo.turno_estado_id].id,
                    nombre=estados[ultimo_turno_atendiendo.turno_estado_id].nombre,
                ),
                turno_tipo=TurnoTipoOut(
                    id=tipos[ultimo_turno_atendiendo.turno_tipo_id].id,
                    nombre=tipos[ultimo_turno_atendiendo.turno_tipo_id].nombre,
                    nivel=tipos[ultimo_turno_atendiendo.turno_tipo_id].nivel,
                ),
                unidad=UnidadOut(
                    id=unidades[ultimo_turno_atendiendo.unidad_id].id,
                    nombre=unidades[ultimo_turno_atendiendo.unidad_id].nombre,
                    clave=unidades[ultimo_turno_atendiendo.unidad_id].clave,
                ),
                ubicacion=UbicacionOut(
                    id=ultimo_turno_atendiendo.ubicacion_id,
                    nombre=ultimo_turno_atendiendo.ubicacion.nombre,
                    numero=ultimo_turno_atendiendo.ubicacion.numero,
                ),
            )
        else:
            ultimo_turno = None

        # Entregar JSON
        return OneListTurnosOut(
            success=True,
            message="Se han consultado todos los turnos",
            data=ListTurnosOut(
                ultimo_turno=ultimo_turno,
                turnos=[
                    TurnoUnidadOut(
                        turno_id=turno.id,
                        turno_numero=turno.numero,
                        turno_fecha=turno.creado.isoformat(),
                        turno_numero_cubiculo=turno.numero_cubiculo,
                        turno_telefono=turno.telefono,
                        turno_comentarios=turno.comentarios,
                        turno_estado=TurnoEstadoOut(
                            id=estados[turno.turno_estado_id].id,
                            nombre=estados[turno.turno_estado_id].nombre,
                        ),
                        turno_tipo=TurnoTipoOut(
                            id=tipos[turno.turno_tipo_id].id,
                            nombre=tipos[turno.turno_tipo_id].nombre,
                            nivel=tipos[turno.turno_tipo_id].nivel,
                        ),
                        unidad=UnidadOut(
                            id=unidades[turno.unidad_id].id,
                            nombre=unidades[turno.unidad_id].nombre,
                            clave=unidades[turno.unidad_id].clave,
                        ),
                        ubicacion=UbicacionOut(
                            id=turno.ubicacion_id,
                            nombre=turno.ubicacion.nombre,
                            numero=turno.ubicacion.numero,
                        ),
                    )
                    for turno in turnos
                ],
            ),
        ).model_dump()
