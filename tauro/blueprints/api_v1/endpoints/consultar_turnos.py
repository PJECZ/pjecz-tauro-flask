"""
API v1 Endpoint: Consultar Turnos
"""

from flask_restful import Resource
from sqlalchemy import or_

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import OneListTurnosOut, ListTurnosOut, TurnoUnidadOut, UnidadOut, VentanillaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnos(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO"""

    def get(self) -> OneListTurnosOut:
        """Consultar los turnos EN ESPERA y ATENDIENDO"""

        # Consultar los turnos...
        # - Filtrar por los estados EN ESPERA y ATENDIENDO,
        # - Filtrar por el estatus A (activo),
        # - Y ordenar por el nombre de tipo de turno ATENCION URGENTE, CON CITA, NORMAL y luego por el número
        turnos = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(or_(TurnoEstado.nombre == "EN ESPERA", TurnoEstado.nombre == "ATENDIENDO"))
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
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

        # Consultar Último turno en estado 'ATENDIENDO'
        ultimo_turno_atendiendo = (
            Turno.query.join(TurnoEstado)
            .join(TurnoTipo)
            .filter(TurnoEstado.nombre == "ATENDIENDO")
            .filter(Turno.estatus == "A")
            .order_by(TurnoTipo.nivel, Turno.numero)
            .first()
        )
        if ultimo_turno_atendiendo:
            ultimo_turno = TurnoUnidadOut(
                turno_id=ultimo_turno_atendiendo.id,
                turno_numero=ultimo_turno_atendiendo.numero,
                turno_estado=ultimo_turno_atendiendo.turno_estado.nombre,
                turno_comentarios=ultimo_turno_atendiendo.comentarios,
                unidad=UnidadOut(
                    id=unidades[ultimo_turno_atendiendo.unidad_id].id,
                    nombre=unidades[ultimo_turno_atendiendo.unidad_id].nombre,
                    clave=unidades[ultimo_turno_atendiendo.unidad_id].clave,
                ),
                ventanilla=VentanillaOut(
                    id=ultimo_turno_atendiendo.ventanilla_id,
                    nombre=ultimo_turno_atendiendo.ventanilla.nombre,
                    numero=ultimo_turno_atendiendo.ventanilla.numero,
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
                        turno_estado=turno.turno_estado.nombre,
                        turno_comentarios=turno.comentarios,
                        unidad=UnidadOut(
                            id=unidades[turno.unidad_id].id,
                            nombre=unidades[turno.unidad_id].nombre,
                            clave=unidades[turno.unidad_id].clave,
                        ),
                        ventanilla=VentanillaOut(
                            id=turno.ventanilla_id,
                            nombre=turno.ventanilla.nombre,
                            numero=turno.ventanilla.numero,
                        ),
                    )
                    for turno in turnos
                ],
            ),
        ).model_dump()
