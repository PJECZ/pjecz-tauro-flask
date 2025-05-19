"""
API v1 Endpoint: Consultar Turnos
"""

from flask_restful import Resource
from sqlalchemy import or_

from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import ListTurnosOut, TurnoUnidadOut, UnidadOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnos(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO"""

    @token_required
    def get(self) -> ListTurnosOut:
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
            .order_by(TurnoTipo.nombre, Turno.numero)
            .all()
        )

        # Si no se encuentran turnos, entregar success en verdadero
        if not turnos:
            return ListTurnosOut(
                success=True,
                message="No hay turnos en espera",
            ).model_dump()

        # Consultar Unidades
        unidades_sql = Unidad.query.all()
        unidades = {unidad.id: unidad for unidad in unidades_sql}

        # Entregar JSON
        return ListTurnosOut(
            success=True,
            message="Se han consultado todos los turnos",
            data=[
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
                )
                for turno in turnos
            ],
        ).model_dump()
