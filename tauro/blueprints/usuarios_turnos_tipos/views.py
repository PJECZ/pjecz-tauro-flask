"""
Usuarios_Turnos_Tipos, vistas
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
from tauro.blueprints.usuarios_turnos_tipos.models import UsuarioTurnoTipo
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios_turnos_tipos.forms import UsuarioTurnoTipoForm
from tauro.blueprints.turnos_tipos.models import TurnoTipo


MODULO = "USUARIOS TURNOS TIPOS"

usuarios_turnos_tipos = Blueprint("usuarios_turnos_tipos", __name__, template_folder="templates")


@usuarios_turnos_tipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@usuarios_turnos_tipos.route("/usuarios_turnos_tipos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Usuario-TurnoTipos"""

    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = UsuarioTurnoTipo.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
    # Luego filtrar por columnas de otras tablas
    # if "persona_rfc" in request.form:
    #     consulta = consulta.join(Persona)
    #     consulta = consulta.filter(Persona.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(UsuarioTurnoTipo.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("usuarios_turnos_tipos.detail", usuario_turno_tipo_id=resultado.id),
                },
                "turno_tipo": resultado.turno_tipo.nombre,
                "toggle_estatus": {
                    "id": resultado.id,
                    "es_activo": resultado.es_activo,
                    "url": (
                        url_for("usuarios_turnos_tipos.toggle_estatus_json", usuario_turno_tipo_id=resultado.id)
                        if current_user.can_admin(MODULO)
                        else ""
                    ),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios_turnos_tipos.route("/usuarios_turnos_tipos/<int:usuario_turno_tipo_id>")
def detail(usuario_turno_tipo_id):
    """Detalle de un Usuario-TurnoTipo"""
    usuario_turno_tipo = UsuarioTurnoTipo.query.get_or_404(usuario_turno_tipo_id)
    return render_template("usuarios_turnos_tipos/detail.jinja2", usuario_turno_tipo=usuario_turno_tipo)


@usuarios_turnos_tipos.route("/usuarios_turnos_tipos/nuevo/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_usuario(usuario_id):
    """Nuevo Usuario-TurnoTipo"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioTurnoTipoForm()
    if form.validate_on_submit():
        # Validación
        es_valido = True

        # Validar si este usuario ya tiene asignado este mismo tipo de turno
        tipo_turno_repetido = (
            UsuarioTurnoTipo.query.filter_by(usuario_id=usuario_id).filter_by(turno_tipo_id=form.turno_tipo.data).first()
        )
        if tipo_turno_repetido is not None:
            es_valido = False
            flash("Este usuario ya tiene asignado este mismo tipo de turno", "warning")

        # Guardar si es válido
        if es_valido:
            usuario_turno_tipo = UsuarioTurnoTipo(
                usuario=usuario,
                turno_tipo_id=form.turno_tipo.data,
                es_activo=form.es_activo.data,
            )
            usuario_turno_tipo.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(
                    f"Nuevo Usuario-TurnoTipo {usuario_turno_tipo.usuario.nombre} - {usuario_turno_tipo.turno_tipo.nombre}"
                ),
                url=url_for("usuarios_turnos_tipos.detail", usuario_turno_tipo_id=usuario_turno_tipo.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.usuario.data = usuario.nombre
    return render_template(
        "usuarios_turnos_tipos/new_with_usuario.jinja2",
        form=form,
        usuario=usuario,
        turnos_tipos=TurnoTipo.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
    )


@usuarios_turnos_tipos.route("/usuarios_turnos_tipos/toggle_estatus_json/<int:usuario_turno_tipo_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def toggle_estatus_json(usuario_turno_tipo_id):
    """Cambiar el estatus de un usuario-rol por solicitud de botón en datatable"""

    # Consultar usuario-rol
    usuario_turno_tipo = UsuarioTurnoTipo.query.get_or_404(usuario_turno_tipo_id)
    if usuario_turno_tipo is None:
        return {"success": False, "message": "No encontrado"}

    # Cambiar estatus a su opuesto
    if usuario_turno_tipo.es_activo:
        usuario_turno_tipo.es_activo = False
    else:
        usuario_turno_tipo.es_activo = True

    # Guardar
    usuario_turno_tipo.save()

    # Entregar JSON
    return {
        "success": True,
        "message": "Activo" if usuario_turno_tipo.estatus else "Inactivo",
        "es_activo": usuario_turno_tipo.es_activo,
        "id": usuario_turno_tipo.id,
    }
