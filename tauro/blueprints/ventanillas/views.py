"""
Ventanillas, vistas
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
from tauro.blueprints.ventanillas.models import Ventanilla

MODULO = "VENTANILLAS"

ventanillas = Blueprint("ventanillas", __name__, template_folder="templates")


@ventanillas.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@ventanillas.route("/ventanillas/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Ventanillas"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Ventanilla.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    # if "persona_id" in request.form:
    #     consulta = consulta.filter_by(persona_id=request.form["persona_id"])
    # Luego filtrar por columnas de otras tablas
    # if "persona_rfc" in request.form:
    #     consulta = consulta.join(Persona)
    #     consulta = consulta.filter(Persona.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(Ventanilla.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("ventanillas.detail", ventanilla_id=resultado.id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@ventanillas.route("/ventanillas")
def list_active():
    """Listado de Ventanillas activos"""
    return render_template(
        "ventanillas/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Ventanillas",
        estatus="A",
    )


@ventanillas.route("/ventanillas/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Ventanillas inactivas"""
    return render_template(
        "ventanillas/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Ventanillas inactivas",
        estatus="B",
    )


@ventanillas.route("/ventanillas/<int:ventanilla_id>")
def detail(ventanilla_id):
    """Detalle de un Ventanilla"""
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    return render_template("ventanillas/detail.jinja2", ventanilla=ventanilla)


# TODO: NEW

# TODO: EDIT


@ventanillas.route("/ventanillas/eliminar/<int:ventanilla_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(ventanilla_id):
    """Eliminar Ventanilla"""
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    if ventanilla.estatus == "A":
        ventanilla.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Ventanilla {ventanilla.clave}"),
            url=url_for("ventanillas.detail", ventanilla_id=ventanilla.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ventanillas.detail", ventanilla_id=ventanilla.id))


@ventanillas.route("/ventanillas/recuperar/<int:ventanilla_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(ventanilla_id):
    """Recuperar Ventanilla"""
    ventanilla = Ventanilla.query.get_or_404(ventanilla_id)
    if ventanilla.estatus == "B":
        ventanilla.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Ventanilla {ventanilla.clave}"),
            url=url_for("ventanillas.detail", ventanilla_id=ventanilla.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ventanillas.detail", ventanilla_id=ventanilla.id))
