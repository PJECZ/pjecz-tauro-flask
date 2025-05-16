"""
Unidades_Ventanillas, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import permission_required
from tauro.blueprints.unidades_ventanillas.models import UnidadVentanilla
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.ventanillas.models import Ventanilla

MODULO = "UNIDADES VENTANILLAS"

unidades_ventanillas = Blueprint("unidades_ventanillas", __name__, template_folder="templates")


@unidades_ventanillas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@unidades_ventanillas.route("/unidades_ventanillas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Unidades-Ventanillas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UnidadVentanilla.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(UnidadVentanilla.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(UnidadVentanilla.estatus == "A")
    if "unidad_id" in request.form:
        consulta = consulta.filter(UnidadVentanilla.unidad_id == request.form["unidad_id"])
    if "ventanilla_id" in request.form:
        consulta = consulta.filter(UnidadVentanilla.ventanilla_id == request.form["ventanilla_id"])
    # Luego filtrar por columnas de otras tablas
    if "ventanilla_nombre" in request.form:
        ventanilla_nombre = safe_string(request.form["ventanilla_nombre"])
        if ventanilla_nombre:
            consulta = consulta.join(Ventanilla)
            consulta = consulta.filter(Ventanilla.nombre.contains(ventanilla_nombre))
    # Ordenar y paginar
    registros = consulta.order_by(UnidadVentanilla.id).offset(start).limit(rows_per_page).all()
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
                "ventanilla": {
                    "nombre": (
                        resultado.ventanilla.nombre + " - " + str(resultado.ventanilla.numero)
                        if resultado.ventanilla.numero
                        else resultado.ventanilla.nombre
                    ),
                    "url": url_for("ventanillas.detail", ventanilla_id=resultado.ventanilla.id),
                },
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@unidades_ventanillas.route("/unidades_ventanillas")
def list_active():
    """Listado de Unidades-Ventanillas activos"""
    return render_template(
        "unidades_ventanillas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Unidades-Ventanillas",
        unidades=Unidad.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        estatus="A",
    )


@unidades_ventanillas.route("/unidades_ventanillas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Unidades-Ventanillas inactivos"""
    return render_template(
        "unidades_ventanillas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Unidades-Ventanillas inactivos",
        unidades=Unidad.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        estatus="B",
    )
