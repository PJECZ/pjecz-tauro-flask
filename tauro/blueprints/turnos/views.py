"""
Turnos, vistas
"""

import json
from datetime import datetime, date, time
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import permission_required
from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos.forms import TurnoForm
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.ventanillas.models import Ventanilla
from tauro.blueprints.unidades.models import Unidad

from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.turnos_estados.models import TurnoEstado

MODULO = "TURNOS"

turnos = Blueprint("turnos", __name__, template_folder="templates")


@turnos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@turnos.route("/turnos/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Turnos"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Turno.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(Turno.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(Turno.estatus == "A")
    if "turno_id" in request.form:
        turno_id = safe_string(request.form["turno_id"])
        if turno_id.isnumeric():
            consulta = consulta.filter(Turno.id == turno_id)
    if "fecha_inicio" in request.form:
        fecha_inicio = request.form["fecha_inicio"]
        if fecha_inicio:
            consulta = consulta.filter(Turno.creado >= fecha_inicio)
    if "fecha_termino" in request.form:
        fecha_termino = request.form["fecha_termino"]
        if fecha_termino:
            consulta = consulta.filter(Turno.creado <= fecha_termino)
    if "unidad_id" in request.form:
        consulta = consulta.filter(Turno.unidad_id == request.form["unidad_id"])
    if "ventanilla_id" in request.form:
        consulta = consulta.filter(Turno.ventanilla_id == request.form["ventanilla_id"])
    if "turno_tipo_id" in request.form:
        consulta = consulta.filter(Turno.turno_tipo_id == request.form["turno_tipo_id"])
    if "turno_estado_id" in request.form:
        consulta = consulta.filter(Turno.turno_estado_id == request.form["turno_estado_id"])
    # Luego filtrar por columnas de otras tablas
    # if "turno_tipo_id" in request.form:
    #     consulta = consulta.join(TurnoTipo)
    #     consulta = consulta.filter(TurnoTipo.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(Turno.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Consultar Unidades
    unidades_sql = Unidad.query.all()
    unidades = {unidad.id: unidad for unidad in unidades_sql}

    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "numero": resultado.id,
                    "url": url_for("turnos.detail", turno_id=resultado.id),
                },
                "numero": f"{resultado.numero}".zfill(3),
                "fecha_hora": resultado.creado.strftime("%Y-%m-%d %H:%M"),
                "tipo": resultado.turno_tipo.nombre,
                "estado": resultado.turno_estado.nombre,
                "unidad": {
                    "nombre": unidades[resultado.unidad_id].clave,
                    "url": url_for("unidades.detail", unidad_id=resultado.unidad_id),
                },
                "ventanilla": {
                    "nombre": (
                        resultado.ventanilla.nombre + f"{ - resultado.ventanilla.numero}"
                        if resultado.ventanilla.numero is not None
                        else ""
                    ),
                    "url": url_for("ventanillas.detail", ventanilla_id=resultado.ventanilla_id),
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@turnos.route("/turnos")
def list_active():
    """Listado de Turnos activos"""
    return render_template(
        "turnos/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Turnos",
        turnos_tipos=TurnoTipo.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoTipo.nombre).all(),
        turnos_estados=TurnoEstado.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoEstado.nombre).all(),
        unidades=Unidad.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        ventanillas=Ventanilla.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        estatus="A",
    )


@turnos.route("/turnos/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Turnos inactivos"""
    return render_template(
        "turnos/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        turnos_tipos=TurnoTipo.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoTipo.nombre).all(),
        turnos_estados=TurnoEstado.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoEstado.nombre).all(),
        unidades=Unidad.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        ventanillas=Ventanilla.query.filter_by(estatus="A").filter_by(es_activo=True).all(),
        titulo="Turnos inactivos",
        estatus="B",
    )


@turnos.route("/turnos/<int:turno_id>")
def detail(turno_id):
    """Detalle de un Turno"""
    turno = Turno.query.get_or_404(turno_id)
    # Consultar Unidades
    unidades_sql = Unidad.query.all()
    unidades = {unidad.id: unidad for unidad in unidades_sql}
    # Entregar resultado
    return render_template("turnos/detail.jinja2", turno=turno, unidades=unidades)


@turnos.route("/turnos/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Turno"""
    form = TurnoForm()
    if form.validate_on_submit():
        # Validar que existan valores NO DEFINIDO
        usuario_no_definido = Usuario.query.filter_by(nombres="NO DEFINIDO").first()
        if usuario_no_definido is None:
            flash("ADVERTENCIA: Se necesita definir un usuario con nombre NO DEFINIDO", "warning")
            return render_template("turnos/new.jinja2", form=form)
        ventanilla_no_definido = Ventanilla.query.filter_by(clave="ND").first()
        if ventanilla_no_definido is None:
            flash("ADVERTENCIA: Se necesita definir una ventanilla con clave ND", "warning")
            return render_template("turnos/new.jinja2", form=form)
        # Calcular el siguiente número - se reinicia la cuenta por día.
        fecha_hoy_inicio = datetime.combine(date.today(), time(0, 0, 0))
        turno_ultimo = Turno.query.filter(Turno.creado >= fecha_hoy_inicio).order_by(Turno.id.desc()).first()
        numero_turno = 0
        if turno_ultimo:
            numero_turno = turno_ultimo.numero
        # Crear registro
        turno = Turno(
            usuario=usuario_no_definido,
            ventanilla=ventanilla_no_definido,
            numero=numero_turno + 1,
            turno_tipo=form.turno_tipo.data,
            inicio=datetime.now(),
            estado="EN_ESPERA",
            comentarios=safe_string(form.comentarios.data),
        )
        turno.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nuevo Turno {turno.id}"),
            url=url_for("turnos.detail", turno_id=turno.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return render_template("turnos/new.jinja2", form=form)


@turnos.route("/turnos/edicion/<int:turno_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(turno_id):
    """Editar Turno"""
    turno = Turno.query.get_or_404(turno_id)
    form = TurnoForm()
    if form.validate_on_submit():
        turno.tipo = form.tipo.data
        turno.comentarios = safe_string(form.comentarios.data)
        turno.save()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado Turno {turno.id}"),
            url=url_for("turnos.detail", turno_id=turno.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.tipo.data = turno.tipo
    form.comentarios.data = turno.comentarios
    return render_template("turnos/edit.jinja2", form=form, turno=turno)


@turnos.route("/turnos/eliminar/<int:turno_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(turno_id):
    """Eliminar Turno"""
    turno = Turno.query.get_or_404(turno_id)
    if turno.estatus == "A":
        turno.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Turno {turno.id}"),
            url=url_for("turnos.detail", turno_id=turno.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("turnos.detail", turno_id=turno.id))


@turnos.route("/turnos/recuperar/<int:turno_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(turno_id):
    """Recuperar Turno"""
    turno = Turno.query.get_or_404(turno_id)
    if turno.estatus == "B":
        turno.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Turno {turno.id}"),
            url=url_for("turnos.detail", turno_id=turno.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("turnos.detail", turno_id=turno.id))
