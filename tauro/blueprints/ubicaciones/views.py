"""
Ubicaciones, vistas
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
from tauro.blueprints.ubicaciones.models import Ubicacion
from tauro.blueprints.ubicaciones.forms import UbicacionForm
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.unidades.models import Unidad

MODULO = "UBICACIONES"

ubicaciones = Blueprint("ubicaciones", __name__, template_folder="templates")


@ubicaciones.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@ubicaciones.route("/ubicaciones/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Ubicaciones"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Ubicacion.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "nombre" in request.form:
        nombre = safe_string(request.form["nombre"], save_enie=True)
        if nombre != "":
            consulta = consulta.filter(Ubicacion.nombre.contains(nombre))
    # Luego filtrar por columnas de otras tablas
    # if "persona_rfc" in request.form:
    #     consulta = consulta.join(Persona)
    #     consulta = consulta.filter(Persona.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(Ubicacion.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("ubicaciones.detail", ubicacion_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "numero": resultado.numero,
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@ubicaciones.route("/ubicaciones")
def list_active():
    """Listado de Ubicaciones activos"""
    return render_template(
        "ubicaciones/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Ubicaciones",
        estatus="A",
    )


@ubicaciones.route("/ubicaciones/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Ubicaciones inactivas"""
    return render_template(
        "ubicaciones/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Ubicaciones inactivas",
        estatus="B",
    )


@ubicaciones.route("/ubicaciones/<int:ubicacion_id>")
def detail(ubicacion_id):
    """Detalle de un Ubicacion"""
    ubicacion = Ubicacion.query.get_or_404(ubicacion_id)
    return render_template("ubicaciones/detail.jinja2", ubicacion=ubicacion)


@ubicaciones.route("/ubicaciones/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Ubicacion"""
    form = UbicacionForm()
    if form.validate_on_submit():
        # Validar que la clave no se repita
        nombre = safe_string(form.nombre.data)
        if Ubicacion.query.filter_by(nombre=nombre).first():
            flash("El nombre ya está en uso. Debe de ser único.", "warning")
            return render_template("ubicaciones/new.jinja2", form=form)
        # Guardar
        ubicacion = Ubicacion(
            nombre=safe_string(form.nombre.data),
            numero=form.numero.data,
            es_activo=form.es_activo.data,
        )
        ubicacion.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva Ubicacion {ubicacion.nombre}"),
            url=url_for("ubicaciones.detail", ubicacion_id=ubicacion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("ubicaciones/new.jinja2", form=form)


@ubicaciones.route("/ubicaciones/edicion/<int:ubicacion_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(ubicacion_id):
    """Editar Ubicacion"""
    ubicacion = Ubicacion.query.get_or_404(ubicacion_id)
    form = UbicacionForm()
    if form.validate_on_submit():
        ubicacion.nombre = safe_string(form.nombre.data)
        ubicacion.numero = form.numero.data
        ubicacion.es_activo = form.es_activo.data
        ubicacion.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Ubicacion {ubicacion.nombre}"),
            url=url_for("ubicaciones.detail", ubicacion_id=ubicacion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.nombre.data = ubicacion.nombre
    form.numero.data = ubicacion.numero
    form.es_activo.data = ubicacion.es_activo
    return render_template("ubicaciones/edit.jinja2", form=form, ubicacion=ubicacion)


@ubicaciones.route("/ubicaciones/eliminar/<int:ubicacion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(ubicacion_id):
    """Eliminar Ubicacion"""
    ubicacion = Ubicacion.query.get_or_404(ubicacion_id)
    if ubicacion.estatus == "A":
        ubicacion.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Ubicacion {ubicacion.clave}"),
            url=url_for("ubicaciones.detail", ubicacion_id=ubicacion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ubicaciones.detail", ubicacion_id=ubicacion.id))


@ubicaciones.route("/ubicaciones/recuperar/<int:ubicacion_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(ubicacion_id):
    """Recuperar Ubicacion"""
    ubicacion = Ubicacion.query.get_or_404(ubicacion_id)
    if ubicacion.estatus == "B":
        ubicacion.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Ubicacion {ubicacion.clave}"),
            url=url_for("ubicaciones.detail", ubicacion_id=ubicacion.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("ubicaciones.detail", ubicacion_id=ubicacion.id))
