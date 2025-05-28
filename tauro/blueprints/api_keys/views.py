"""
API-Keys, vistas
"""

import json
import uuid
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import permission_required
from tauro.blueprints.api_keys.models import APIKey

from tauro.blueprints.api_keys.forms import APIKeyForm

MODULO = "API KEYS"

api_keys = Blueprint("api_keys", __name__, template_folder="templates")


@api_keys.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@api_keys.route("/api_keys/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de API Keys"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = APIKey.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "ApiKey" in request.form:
        api_key = safe_string(request.form["ApiKey"])
        if api_key:
            consulta = consulta.filter(APIKey.api_key.contains(api_key))
    # Luego filtrar por columnas de otras tablas
    # if "persona_rfc" in request.form:
    #     consulta = consulta.join(Persona)
    #     consulta = consulta.filter(Persona.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(APIKey.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "api_key": resultado.api_key,
                    "url": url_for("api_keys.detail", api_key_id=resultado.id),
                },
                "api_key_expiracion": resultado.api_key_expiracion.strftime("%Y-%m-%d %H:%M:%S"),
                "es_activo": resultado.es_activo,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@api_keys.route("/api_keys")
def list_active():
    """Listado de API Keys activos"""
    return render_template(
        "api_keys/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="API Keys",
        estatus="A",
    )


@api_keys.route("/api_keys/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de API Keys inactivos"""
    return render_template(
        "api_keys/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="API Keys inactivos",
        estatus="B",
    )


@api_keys.route("/api_keys/<int:api_key_id>")
def detail(api_key_id):
    """Detalle de un API Keys"""
    api_key = APIKey.query.get_or_404(api_key_id)
    return render_template("api_keys/detail.jinja2", api_key=api_key)


@api_keys.route("/api_keys/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva API Key"""
    form = APIKeyForm()
    if form.validate_on_submit():
        api_key = APIKey(
            api_key=safe_string(form.api_key.data),
            api_key_expiracion=form.api_key_expiracion.data,
            es_activo=form.es_activo.data,
        )
        api_key.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva API Key {api_key.id}"),
            url=url_for("api_keys.detail", api_key_id=api_key.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Carga de datos por defecto
    form.api_key.data = uuid.uuid4().hex
    form.api_key_expiracion.data = datetime.now() + timedelta(days=365 * 5)
    form.es_activo.data = True
    return render_template("api_keys/new.jinja2", form=form)


@api_keys.route("/api_keys/edicion/<int:api_key_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(api_key_id):
    """Editar API Key"""
    api_key = APIKey.query.get_or_404(api_key_id)
    form = APIKeyForm()
    if form.validate_on_submit():
        api_key.api_key = safe_string(form.api_key.data)
        api_key.api_key_expiracion = form.api_key_expiracion.data
        api_key.es_activo = form.es_activo.data
        api_key.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado API Key {api_key.api_key}"),
            url=url_for("api_keys.detail", api_key_id=api_key.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.api_key.data = api_key.api_key
    form.api_key_expiracion.data = api_key.api_key_expiracion
    form.es_activo.data = api_key.es_activo
    return render_template("api_keys/edit.jinja2", form=form, api_key=api_key)


@api_keys.route("/api_keys/eliminar/<int:api_key_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(api_key_id):
    """Eliminar API Key"""
    api_key = APIKey.query.get_or_404(api_key_id)
    if api_key.estatus == "A":
        api_key.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado API Key {api_key.id}"),
            url=url_for("api_keys.detail", api_key_id=api_key.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("api_keys.detail", api_key_id=api_key.id))


@api_keys.route("/api_keys/recuperar/<int:api_key_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(api_key_id):
    """Recuperar API Key"""
    api_key = APIKey.query.get_or_404(api_key_id)
    if api_key.estatus == "B":
        api_key.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado API Key {api_key.id}"),
            url=url_for("api_keys.detail", api_key_id=api_key.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("api_keys.detail", api_key_id=api_key.id))
