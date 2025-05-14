"""
Turnos_Tipos, vistas
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
from tauro.blueprints.turnos_tipos.models import TurnoTipo

from tauro.blueprints.turnos_tipos.forms import TurnoTipoForm

MODULO = "TURNOS TIPOS"

turnos_tipos = Blueprint("turnos_tipos", __name__, template_folder="templates")


@turnos_tipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@turnos_tipos.route("/turnos_tipos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Turnos Tipos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = TurnoTipo.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"])
        if nombre:
            consulta = consulta.filter(TurnoTipo.nombre.contains(nombre))
    # Luego filtrar por columnas de otras tablas
    # if "persona_rfc" in request.form:
    #     consulta = consulta.join(Persona)
    #     consulta = consulta.filter(Persona.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(TurnoTipo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("turnos_tipos.detail", turno_tipo_id=resultado.id),
                },
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@turnos_tipos.route("/turnos_tipos")
def list_active():
    """Listado de Turnos Tipos activos"""
    return render_template(
        "turnos_tipos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Turnos Tipos",
        estatus="A",
    )


@turnos_tipos.route("/turnos_tipos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Turnos Tipos inactivos"""
    return render_template(
        "turnos_tipos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Turnos Tipos inactivos",
        estatus="B",
    )


@turnos_tipos.route("/turnos_tipos/<int:turno_tipo_id>")
def detail(turno_tipo_id):
    """Detalle de un Turno Tipo"""
    turno_tipo = TurnoTipo.query.get_or_404(turno_tipo_id)
    return render_template("turnos_tipos/detail.jinja2", turno_tipo=turno_tipo)


@turnos_tipos.route("/turnos_tipos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Turno Tipo"""
    form = TurnoTipoForm()
    if form.validate_on_submit():
        turno_tipo = TurnoTipo(nombre=safe_string(form.nombre.data))
        turno_tipo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Turno Tipo {turno_tipo.nombre}"),
            url=url_for("turnos_tipos.detail", turno_tipo_id=turno_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("turnos_tipos/new.jinja2", form=form)


@turnos_tipos.route("/turnos_tipos/edicion/<int:turno_tipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(turno_tipo_id):
    """Editar Turno Tipo"""
    turno_tipo = TurnoTipo.query.get_or_404(turno_tipo_id)
    form = TurnoTipoForm()
    if form.validate_on_submit():
        turno_tipo.nombre = safe_string(form.nombre.data)
        turno_tipo.es_activo = form.es_activo.data
        turno_tipo.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Turno Tipo {turno_tipo.nombre}"),
            url=url_for("turnos_tipos.detail", turno_tipo_id=turno_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(url_for("turnos_tipos.list_active"))
    form.nombre.data = turno_tipo.nombre
    form.es_activo.data = turno_tipo.es_activo
    return render_template("turnos_tipos/edit.jinja2", form=form, turno_tipo=turno_tipo)


@turnos_tipos.route("/turnos_tipos/eliminar/<int:turno_tipo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(turno_tipo_id):
    """Eliminar Turno Tipo"""
    turno_tipo = TurnoTipo.query.get_or_404(turno_tipo_id)
    if turno_tipo.estatus == "A":
        turno_tipo.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Turno Tipo {turno_tipo.nombre}"),
            url=url_for("turnos_tipos.detail", turno_tipo_id=turno_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("turnos_tipos.detail", turno_tipo_id=turno_tipo.id))


@turnos_tipos.route("/turnos_tipos/recuperar/<int:turno_tipo_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(turno_tipo_id):
    """Recuperar Turno Tipo"""
    turno_tipo = TurnoTipo.query.get_or_404(turno_tipo_id)
    if turno_tipo.estatus == "B":
        turno_tipo.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Turno Tipo {turno_tipo.nombre}"),
            url=url_for("turnos_tipos.detail", turno_tipo_id=turno_tipo.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("turnos_tipos.detail", turno_tipo_id=turno_tipo.id))
