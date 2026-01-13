"""
API v1 Endpoint: Consultar Turnos Unidad
"""

from flask import current_app
from flask_restful import Resource
from sqlalchemy import or_

from tauro.blueprints.api_oauth2_v1.schemas import OneUnidadTurnosOut, TurnoOut, UnidadOut, UnidadTurnosOut, UbicacionOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnosUnidad(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

    def get(self, unidad_id: int) -> OneUnidadTurnosOut:
        """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad, aquí NO SE USA el decorador porque es para pantallas"""

        # Validar el ID de la unidad
        unidad = Unidad.query.get(unidad_id)
        if unidad is None:
            return OneUnidadTurnosOut(
                success=False,
                message="Unidad no encontrada",
            ).model_dump()

        # Consultar los turnos...
        # - Filtrar por unidad,
        # - Filtrar por los estados EN ESPERA y ATENDIENDO,
        # - Filtrar por el estatus A (activo),
        # - Y ordenar por el nombre de tipo de turno ATENCION URGENTE, CON CITA, NORMAL y luego por el número del turno
        turnos = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(Turno.unidad_id == unidad.id)
            .filter(TurnoEstado.nombre != "COMPLETADO", TurnoEstado.nombre != "CANCELADO")
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .limit(current_app.config["LIMITE_DE_TURNOS_LISTADOS"])
            .all()
        )

        # Si no se encuentran turnos, entregar success en verdadero
        if not turnos:
            return OneUnidadTurnosOut(
                success=True,
                message="No hay turnos en espera",
                data=UnidadTurnosOut(
                    unidad=UnidadOut(id=unidad.id, clave=unidad.clave, nombre=unidad.nombre), ultimo_turno=None, turnos=[]
                ),
            ).model_dump()

        # Consultar Último turno en estado 'ATENDIENDO'
        ultimo_turno_atendiendo = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(Turno.unidad_id == unidad.id)
            .filter(or_(TurnoEstado.nombre == "ATENDIENDO", TurnoEstado.nombre == "ATENDIENDO EN CUBICULO"))
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .first()
        )
        if ultimo_turno_atendiendo:
            ultimo_turno = TurnoOut(
                turno_id=ultimo_turno_atendiendo.id,
                turno_numero=ultimo_turno_atendiendo.numero,
                turno_fecha=ultimo_turno_atendiendo.creado.isoformat(),
                turno_estado=ultimo_turno_atendiendo.turno_estado.nombre,
                turno_tipo_id=ultimo_turno_atendiendo.turno_tipo_id,
                turno_numero_cubiculo=ultimo_turno_atendiendo.numero_cubiculo,
                turno_telefono=ultimo_turno_atendiendo.telefono,
                turno_comentarios=ultimo_turno_atendiendo.comentarios,
                ubicacion=UbicacionOut(
                    id=ultimo_turno_atendiendo.ubicacion.id,
                    nombre=ultimo_turno_atendiendo.ubicacion.nombre,
                    numero=ultimo_turno_atendiendo.ubicacion.numero,
                ),
                unidad=UnidadOut(id=unidad.id, clave=unidad.clave, nombre=unidad.nombre),
            )
        else:
            ultimo_turno = None

        # Entregar JSON
        return OneUnidadTurnosOut(
            success=True,
            message=f"Se han consultado los turnos de {unidad.clave}",
            data=UnidadTurnosOut(
                unidad=UnidadOut(id=unidad.id, clave=unidad.clave, nombre=unidad.nombre),
                ultimo_turno=ultimo_turno,
                turnos=[
                    TurnoOut(
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
                        unidad=UnidadOut(id=unidad.id, clave=unidad.clave, nombre=unidad.nombre),
                    )
                    for turno in turnos
                ],
            ),
        ).model_dump()
