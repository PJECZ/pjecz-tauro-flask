"""
Unidades Ubicaciones, vistas
"""

import json
from flask import Blueprint, render_template, request, url_for
from flask_login import login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string

from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import permission_required
from tauro.blueprints.unidades_ubicaciones.models import UnidadUbicacion
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.ubicaciones.models import Ubicacion

MODULO = "UNIDADES UBICACIONES"

unidades_ubicaciones = Blueprint("unidades_ubicaciones", __name__, template_folder="templates")


@unidades_ubicaciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@unidades_ubicaciones.route("/unidades_ubicaciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Unidades-Ubicaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UnidadUbicacion.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(UnidadUbicacion.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(UnidadUbicacion.estatus == "A")
    if "unidad_id" in request.form:
        consulta = consulta.filter(UnidadUbicacion.unidad_id == request.form["unidad_id"])
    if "ubicacion_id" in request.form:
        consulta = consulta.filter(UnidadUbicacion.ubicacion_id == request.form["ubicacion_id"])
    # Luego filtrar por columnas de otras tablas
    if "ubicacion_nombre" in request.form:
        ubicacion_nombre = safe_string(request.form["ubicacion_nombre"])
        if ubicacion_nombre:
            consulta = consulta.join(Ubicacion)
            consulta = consulta.filter(Ubicacion.nombre.contains(ubicacion_nombre))
    # Ordenar y paginar
    registros = consulta.order_by(UnidadUbicacion.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": resultado.id,
                "unidad": {
                    "nombre": resultado.unidad.clave + ": " + resultado.unidad.nombre,
                    "url": url_for("unidades.detail", unidad_id=resultado.unidad.id),
                },
                "ubicacion": {
                    "nombre": (
                        resultado.ubicacion.nombre + " - " + str(resultado.ubicacion.numero)
                        if resultado.ubicacion.numero
                        else resultado.ubicacion.nombre
                    ),
                    "url": url_for("ubicaciones.detail", ubicacion_id=resultado.ubicacion.id),
                },
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@unidades_ubicaciones.route("/unidades_ubicaciones")
def list_active():
    """Listado de Unidades-Ubicaciones activos"""
    return render_template(
        "unidades_ubicaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Unidades-Ubicaciones",
        unidades=Unidad.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        estatus="A",
    )


@unidades_ubicaciones.route("/unidades_ubicaciones/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Unidades-Ubicaciones inactivos"""
    return render_template(
        "unidades_ubicaciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Unidades-Ubicaciones inactivos",
        unidades=Unidad.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        estatus="B",
    )
