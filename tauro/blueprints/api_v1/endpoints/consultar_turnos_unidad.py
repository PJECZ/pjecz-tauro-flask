"""
API v1 Endpoint: Consultar Turnos Unidad
"""

from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from lib.safe_string import safe_clave
from tauro.blueprints.api_v1.endpoints.autenticar import token_required
from tauro.blueprints.api_v1.schemas import ListTurnoSchemaOut, TurnoSchemaOut
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.unidades.models import Unidad


class ConsultarTurnosUnidad(Resource):
    """Consultar los turnos EN ESPERA y ATENDIENDO de una unidad"""

    @token_required
    def get(self, unidad_clave: str = None) -> ListTurnoSchemaOut:
        """Consultar turnos"""
        # Validar la clave de la unidad
        unidad = None
        if unidad_clave is not None:
            unidad_clave = safe_clave(unidad_clave)
            if unidad_clave == "":
                return ListTurnoSchemaOut(
                    success=False,
                    message="La clave de la unidad no es válida",
                ).model_dump()
            try:
                unidad = Unidad.query.filter_by(clave=unidad_clave).filter_by(estatus="A").one()
            except (MultipleResultsFound, NoResultFound):
                return ListTurnoSchemaOut(
                    success=False,
                    message="Unidad no encontrada",
                ).model_dump()
        # Consultar los turnos
        turnos = Turno.query.join(TurnoEstado).join(TurnoTipo)
        # Si se recibe la clave de la unidad, filtrar por unidad
        if unidad is not None:
            turnos = turnos.filter(Turno.unidad_id == unidad.id)
        # Filtrar por los estados EN ESPERA y ATENDIENDO,
        turnos = turnos.filter(or_(TurnoEstado.nombre == "EN ESPERA", TurnoEstado.nombre == "ATENDIENDO"))
        # Filtrar por el estatus A (activo)
        turnos = turnos.filter(Turno.estatus == "A")
        # Ordenar por el nombre de tipo de turno ATENCION URGENTE, CON CITA, NORMAL y luego por el número del turno
        turnos = turnos.order_by(TurnoTipo.nombre, Turno.numero)
        # Realizar la consulta
        turnos = turnos.all()
        # Si no se encuentran turnos, retornar un mensaje
        if not turnos:
            return ListTurnoSchemaOut(
                success=True,
                message="No hay turnos en espera",
            ).model_dump()
        # Entregar JSON
        return ListTurnoSchemaOut(
            success=True,
            message="Se han consultado todos los turnos",
            data=[TurnoSchemaOut(id=turno.id, numero=turno.numero, comentarios=turno.comentarios) for turno in turnos],
        ).model_dump()
