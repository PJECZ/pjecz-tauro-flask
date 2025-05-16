"""
Turnos_Estados, vistas
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
from tauro.blueprints.turnos_estados.models import TurnoEstado

from tauro.blueprints.turnos_estados.forms import TurnoEstadoForm

MODULO = "TURNOS ESTADOS"

turnos_estados = Blueprint("turnos_estados", __name__, template_folder="templates")


@turnos_estados.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@turnos_estados.route("/turnos_estados/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Turnos Estados"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = TurnoEstado.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"])
        if nombre:
            consulta = consulta.filter(TurnoEstado.nombre.contains(nombre))
    # Luego filtrar por columnas de otras tablas
    # if "persona_rfc" in request.form:
    #     consulta = consulta.join(Persona)
    #     consulta = consulta.filter(Persona.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(TurnoEstado.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "nombre": resultado.nombre,
                    "url": url_for("turnos_estados.detail", turno_estado_id=resultado.id),
                },
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@turnos_estados.route("/turnos_estados")
def list_active():
    """Listado de Turnos Estados activos"""
    return render_template(
        "turnos_estados/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Turnos Estados",
        estatus="A",
    )


@turnos_estados.route("/turnos_estados/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Turnos Estados inactivos"""
    return render_template(
        "turnos_estados/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Turnos Estados inactivos",
        estatus="B",
    )


@turnos_estados.route("/turnos_estados/<int:turno_estado_id>")
def detail(turno_estado_id):
    """Detalle de un Turno Estado"""
    turno_estado = TurnoEstado.query.get_or_404(turno_estado_id)
    return render_template("turnos_estados/detail.jinja2", turno_estado=turno_estado)


@turnos_estados.route("/turnos_estados/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Turno Estado"""
    form = TurnoEstadoForm()
    if form.validate_on_submit():
        turno_estado = TurnoEstado(
            nombre=safe_string(form.nombre.data),
            es_activo=form.es_activo.data,
        )
        turno_estado.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Turno Estado {turno_estado.nombre}"),
            url=url_for("turnos_estados.detail", turno_estado_id=turno_estado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("turnos_estados/new.jinja2", form=form)


@turnos_estados.route("/turnos_estados/edicion/<int:turno_estado_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(turno_estado_id):
    """Editar Turno Estado"""
    turno_estado = TurnoEstado.query.get_or_404(turno_estado_id)
    form = TurnoEstadoForm()
    if form.validate_on_submit():
        turno_estado.nombre = safe_string(form.nombre.data)
        turno_estado.es_activo = form.es_activo.data
        turno_estado.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Turno Estado {turno_estado.nombre}"),
            url=url_for("turnos_estados.detail", turno_estado_id=turno_estado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(url_for("turnos_estados.list_active"))
    # Cargar datos
    form.nombre.data = turno_estado.nombre
    form.es_activo.data = turno_estado.es_activo
    return render_template("turnos_estados/edit.jinja2", form=form, turno_estado=turno_estado)


@turnos_estados.route("/turnos_estados/eliminar/<int:turno_estado_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(turno_estado_id):
    """Eliminar Turno Estado"""
    turno_estado = TurnoEstado.query.get_or_404(turno_estado_id)
    if turno_estado.estatus == "A":
        turno_estado.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Turno Estado {turno_estado.nombre}"),
            url=url_for("turnos_estados.detail", turno_estado_id=turno_estado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("turnos_estados.detail", turno_estado_id=turno_estado.id))


@turnos_estados.route("/turnos_estados/recuperar/<int:turno_estado_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(turno_estado_id):
    """Recuperar Turno Estado"""
    turno_estado = TurnoEstado.query.get_or_404(turno_estado_id)
    if turno_estado.estatus == "B":
        turno_estado.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Turno Estado {turno_estado.nombre}"),
            url=url_for("turnos_estados.detail", turno_estado_id=turno_estado.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("turnos_estados.detail", turno_estado_id=turno_estado.id))
