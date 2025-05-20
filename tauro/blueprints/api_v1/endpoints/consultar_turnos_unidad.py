"""
API v1 Endpoint: Consultar Turnos Unidad
"""

from flask_restful import Resource
from sqlalchemy import or_

from tauro.blueprints.api_v1.schemas import OneUnidadTurnosOut, TurnoOut, UnidadTurnosOut, UnidadOut, VentanillaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnosUnidad(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

    def get(self, unidad_id: int) -> OneUnidadTurnosOut:
        """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

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
            .filter(or_(TurnoEstado.nombre == "EN ESPERA", TurnoEstado.nombre == "ATENDIENDO"))
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .all()
        )

        # Si no se encuentran turnos, entregar success en verdadero
        if not turnos:
            return OneUnidadTurnosOut(
                success=True,
                message="No hay turnos en espera",
            ).model_dump()

        # Consultar Último turno en estado 'ATENDIENDO'
        ultimo_turno_atendiendo = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(Turno.unidad_id == unidad.id)
            .filter(TurnoEstado.nombre == "ATENDIENDO")
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .first()
        )
        if ultimo_turno_atendiendo:
            ultimo_turno = TurnoOut(
                turno_id=ultimo_turno_atendiendo.id,
                turno_numero=ultimo_turno_atendiendo.numero,
                turno_estado=ultimo_turno_atendiendo.turno_estado.nombre,
                turno_comentarios=ultimo_turno_atendiendo.comentarios,
                ventanilla=VentanillaOut(
                    id=ultimo_turno_atendiendo.ventanilla.id,
                    nombre=ultimo_turno_atendiendo.ventanilla.nombre,
                    numero=ultimo_turno_atendiendo.ventanilla.numero,
                ),
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
                        turno_estado=turno.turno_estado.nombre,
                        turno_comentarios=turno.comentarios,
                        ventanilla=VentanillaOut(
                            id=turno.ventanilla.id,
                            nombre=turno.ventanilla.nombre,
                            numero=turno.ventanilla.numero,
                        ),
                    )
                    for turno in turnos
                ],
            ),
        ).model_dump()
