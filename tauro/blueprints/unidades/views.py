"""
Unidades, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message, safe_clave

from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import permission_required
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.unidades.forms import UnidadForm

MODULO = "UNIDADES"

unidades = Blueprint("unidades", __name__, template_folder="templates")


@unidades.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@unidades.route("/unidades/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Unidad"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Unidad.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "clave" in request.form:
        try:
            clave = safe_clave(request.form["clave"])
            if clave != "":
                consulta = consulta.filter(Unidad.clave.contains(clave))
        except ValueError:
            pass
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(Unidad.nombre.contains(nombre))
    # Ordenar y paginar
    registros = consulta.order_by(Unidad.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("unidades.detail", unidad_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@unidades.route("/unidades")
def list_active():
    """Listado de Unidades activas"""
    return render_template(
        "unidades/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Unidades",
        estatus="A",
    )


@unidades.route("/unidades/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Unidades inactivas"""
    return render_template(
        "unidades/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Unidades inactivas",
        estatus="B",
    )


@unidades.route("/unidades/<int:unidad_id>")
def detail(unidad_id):
    """Detalle de un Unidad"""
    unidad = Unidad.query.get_or_404(unidad_id)
    return render_template("unidades/detail.jinja2", unidad=unidad)


@unidades.route("/unidades/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Unidad"""
    form = UnidadForm()
    if form.validate_on_submit():
        # Validar que la clave no se repita
        clave = safe_clave(form.clave.data)
        if Unidad.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
            return render_template("unidades/new.jinja2", form=form)
        # Guardar
        unidad = Unidad(
            clave=safe_clave(form.clave.data),
            nombre=safe_string(form.nombre.data),
            es_activo=form.es_activo.data,
        )
        unidad.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva Unidad {unidad.clave}"),
            url=url_for("unidades.detail", unidad_id=unidad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("unidades/new.jinja2", form=form)


@unidades.route("/unidades/edicion/<int:unidad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(unidad_id):
    """Editar Unidad"""
    unidad = Unidad.query.get_or_404(unidad_id)
    form = UnidadForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data)
        if unidad.clave != clave:
            unidad_existente = Unidad.query.filter_by(clave=clave).first()
            if unidad_existente and unidad_existente.id != unidad_id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si es válido actualizar
        if es_valido:
            unidad.clave = safe_clave(form.clave.data)
            unidad.nombre = safe_string(form.nombre.data)
            unidad.es_activo = form.es_activo.data
            unidad.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Unidad {unidad.clave}"),
                url=url_for("unidades.detail", unidad_id=unidad.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.clave.data = unidad.clave
    form.nombre.data = unidad.nombre
    form.es_activo.data = unidad.es_activo
    return render_template("unidades/edit.jinja2", form=form, unidad=unidad)


@unidades.route("/unidades/eliminar/<int:unidad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(unidad_id):
    """Eliminar Unidad"""
    unidad = Unidad.query.get_or_404(unidad_id)
    if unidad.estatus == "A":
        unidad.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Unidad {unidad.clave}"),
            url=url_for("unidades.detail", unidad_id=unidad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("unidades.detail", unidad_id=unidad.id))


@unidades.route("/unidades/recuperar/<int:unidad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(unidad_id):
    """Recuperar Unidad"""
    unidad = Unidad.query.get_or_404(unidad_id)
    if unidad.estatus == "B":
        unidad.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Unidad {unidad.clave}"),
            url=url_for("unidades.detail", unidad_id=unidad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("unidades.detail", unidad_id=unidad.id))
