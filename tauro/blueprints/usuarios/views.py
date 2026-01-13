"""
Usuarios, vistas
"""

import json
import re
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from pytz import timezone
from lib.pwgen import generar_contrasena

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_next_url import safe_next_url
from lib.safe_string import CONTRASENA_REGEXP, EMAIL_REGEXP, safe_email, safe_message, safe_string
from tauro.extensions import pwd_context
from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.entradas_salidas.models import EntradaSalida
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import anonymous_required, permission_required
from tauro.blueprints.usuarios.forms import AccesoForm, UsuarioForm
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.ubicaciones.models import Ubicacion

MODULO = "USUARIOS"

usuarios = Blueprint("usuarios", __name__, template_folder="templates")


@usuarios.route("/login", methods=["GET", "POST"])
@anonymous_required()
def login():
    """Acceso al Sistema"""
    form = AccesoForm(siguiente=request.args.get("siguiente"))
    if form.validate_on_submit():
        # Tomar valores del formulario
        identidad = request.form.get("identidad")
        contrasena = request.form.get("contrasena")
        siguiente_url = request.form.get("siguiente")
        # El ingreso es con username/password
        if re.fullmatch(EMAIL_REGEXP, identidad) is None:
            flash("Correo electrónico no válido.", "warning")
        elif re.fullmatch(CONTRASENA_REGEXP, contrasena) is None:
            flash("Contraseña no válida.", "warning")
        else:
            usuario = Usuario.find_by_identity(identidad)
            if usuario and usuario.authenticated(password=contrasena):
                if login_user(usuario, remember=True) and usuario.is_active:
                    EntradaSalida(
                        usuario_id=usuario.id,
                        tipo="INGRESO",
                        direccion_ip=request.remote_addr,
                    ).save()
                    if siguiente_url:
                        return redirect(safe_next_url(siguiente_url))
                    return redirect(url_for("sistemas.start"))
                else:
                    flash("No está activa esa cuenta", "warning")
            else:
                flash("Usuario o contraseña incorrectos.", "warning")
    return render_template(
        "usuarios/login.jinja2",
        form=form,
        title="Sistema de Turnos",
    )


@usuarios.route("/logout")
@login_required
def logout():
    """Salir del Sistema"""
    EntradaSalida(
        usuario_id=current_user.id,
        tipo="SALIO",
        direccion_ip=request.remote_addr,
    ).save()
    logout_user()
    flash("Ha salido de este sistema.", "success")
    return redirect(url_for("usuarios.login"))


@usuarios.route("/perfil")
@login_required
def profile():
    """Mostrar el Perfil"""
    ahora_utc = datetime.now(timezone("UTC"))
    ahora_mx_coah = ahora_utc.astimezone(timezone("America/Mexico_City"))
    formato_fecha = "%Y-%m-%d %H:%M %p"
    return render_template(
        "usuarios/profile.jinja2",
        ahora_utc_str=ahora_utc.strftime(formato_fecha),
        ahora_mx_coah_str=ahora_mx_coah.strftime(formato_fecha),
    )


@usuarios.route("/usuarios/datatable_json", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.VER)
def datatable_json():
    """DataTable JSON para listado de Usuarios"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Usuario.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter(Usuario.estatus == request.form["estatus"])
    else:
        consulta = consulta.filter(Usuario.estatus == "A")
    # Filtrar por las columnas de texto de Usuario
    if "nombres" in request.form:
        consulta = consulta.filter(Usuario.nombres.contains(safe_string(request.form["nombres"])))
    if "apellido_paterno" in request.form:
        consulta = consulta.filter(Usuario.apellido_paterno.contains(safe_string(request.form["apellido_paterno"])))
    if "apellido_materno" in request.form:
        consulta = consulta.filter(Usuario.apellido_materno.contains(safe_string(request.form["apellido_materno"])))
    if "email" in request.form:
        consulta = consulta.filter(Usuario.email.contains(safe_email(request.form["email"], search_fragment=True)))
    if "unidad_id" in request.form:
        consulta = consulta.filter(Usuario.unidad_id == request.form["unidad_id"])
    # Ordenar y paginar
    registros = consulta.order_by(Usuario.email).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "email": resultado.email,
                    "url": url_for("usuarios.detail", usuario_id=resultado.id),
                },
                "nombre": resultado.nombre,
                "ubicacion": {
                    "nombre": resultado.ubicacion.nombre_numero,
                    "url": url_for("ubicaciones.detail", ubicacion_id=resultado.ubicacion.id),
                },
                "acceso_frontend": resultado.es_acceso_frontend,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@usuarios.route("/usuarios")
@login_required
@permission_required(MODULO, Permiso.VER)
def list_active():
    """Listado de Usuarios activos"""
    return render_template(
        "usuarios/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Usuarios",
        estatus="A",
    )


@usuarios.route("/usuarios/inactivos")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de Usuarios inactivos"""
    return render_template(
        "usuarios/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Usuarios inactivos",
        estatus="B",
    )


@usuarios.route("/usuarios/<int:usuario_id>")
@login_required
@permission_required(MODULO, Permiso.VER)
def detail(usuario_id):
    """Detalle de un Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template("usuarios/detail.jinja2", usuario=usuario)


@usuarios.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nuevo Usuario"""
    form = UsuarioForm()
    if form.validate_on_submit():
        # Validaciones
        es_valido = True
        # Validar que el email no se repita
        email = safe_email(form.email.data)
        if Usuario.query.filter_by(email=email).first():
            flash("El e-mail ya está en uso. Debe de ser único.", "warning")
            es_valido = False
        if form.contrasena.data:
            contrasena = pwd_context.hash(form.contrasena.data.strip())
        else:
            contrasena = pwd_context.hash(generar_contrasena())
        # Determinar Ubicacion como NO DEFINIDO
        ubicacion_nd = Ubicacion.query.filter_by(nombre="NO DEFINIDO").first()
        # Guardar
        if es_valido:
            usuario = Usuario(
                email=email,
                nombres=safe_string(form.nombres.data, save_enie=True),
                apellido_paterno=safe_string(form.apellido_paterno.data, save_enie=True),
                apellido_materno=safe_string(form.apellido_materno.data, save_enie=True),
                contrasena=contrasena,
                unidad_id=form.unidad.data,
                es_acceso_frontend=form.es_acceso_frontend.data,
                ubicacion=ubicacion_nd,
            )
            usuario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nuevo Usuario {usuario.email}"),
                url=url_for("usuarios.detail", usuario_id=usuario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # Entregar
    return render_template("usuarios/new.jinja2", form=form)


@usuarios.route("/usuarios/edicion/<int:usuario_id>", methods=["GET", "POST"])
@login_required
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(usuario_id):
    """Editar Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    form = UsuarioForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia el e-mail verificar que no este en uso
        email = safe_email(form.email.data)
        if usuario.email != email:
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente and usuario_existente.id != usuario.id:
                es_valido = False
                flash("La e-mail ya está en uso. Debe de ser único.", "warning")
        # Verificar que la ubicacion seleccionada no este siendo utilizada por alguien más.
        ubicacion_seleccionada_id = form.ubicacion.data
        usuario_ocupando_ubicacion = Usuario.query.filter_by(ubicacion_id=ubicacion_seleccionada_id).first()
        if (
            usuario_ocupando_ubicacion
            and usuario_ocupando_ubicacion.ubicacion.nombre != "NO DEFINIDO"
            and usuario_ocupando_ubicacion.id != usuario.id
        ):
            es_valido = False
            flash(
                f"La ubicacion '{usuario_ocupando_ubicacion.ubicacion.nombre} - {usuario_ocupando_ubicacion.ubicacion.numero}' está siendo utilizada por el usuario {usuario_ocupando_ubicacion.nombre}.",
                "warning",
            )
        # Si es valido actualizar
        if es_valido:
            usuario.email = email
            usuario.nombres = safe_string(form.nombres.data, save_enie=True)
            usuario.apellido_paterno = safe_string(form.apellido_paterno.data, save_enie=True)
            usuario.apellido_materno = safe_string(form.apellido_materno.data, save_enie=True)
            if form.contrasena.data:
                usuario.contrasena = pwd_context.hash(form.contrasena.data.strip())
            usuario.unidad_id = form.unidad.data
            usuario.ubicacion_id = ubicacion_seleccionada_id
            usuario.es_acceso_frontend = form.es_acceso_frontend.data
            usuario.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Usuario {usuario.email}"),
                url=url_for("usuarios.detail", usuario_id=usuario.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    # No es necesario pasar autoridad_id porque se va a tomar de usuario con JS
    # Tampoco es necesario pasar oficina_id porque se va a tomar de usuario con JS
    form.email.data = usuario.email
    form.nombres.data = usuario.nombres
    form.apellido_paterno.data = usuario.apellido_paterno
    form.apellido_materno.data = usuario.apellido_materno
    form.unidad.data = usuario.unidad_id
    form.ubicacion.data = usuario.ubicacion_id
    form.es_acceso_frontend.data = usuario.es_acceso_frontend
    return render_template("usuarios/edit.jinja2", form=form, usuario=usuario)


@usuarios.route("/usuarios/eliminar/<int:usuario_id>")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(usuario_id):
    """Eliminar Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus == "A":
        # Dar de baja al usuario
        usuario.delete()
        # Dar de baja los roles del usuario
        for usuario_rol in usuario.usuarios_roles:
            usuario_rol.delete()
        # Guardar en la bitacora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado Usuario {usuario.email}"),
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("usuarios.detail", usuario_id=usuario.id))


@usuarios.route("/usuarios/recuperar/<int:usuario_id>")
@login_required
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(usuario_id):
    """Recuperar Usuario"""
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.estatus == "B":
        # Recuperar al usuario
        usuario.recover()
        # Recuperar los roles del usuario
        for usuario_rol in usuario.usuarios_roles:
            usuario_rol.recover()
        # Guardar en la bitacora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado Usuario {usuario.email}"),
            url=url_for("usuarios.detail", usuario_id=usuario.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("usuarios.detail", usuario_id=usuario.id))


@usuarios.route("/usuarios/select_json", methods=["GET", "POST"])
def select_json():
    """Select JSON para Usuarios"""
    # Consultar
    consulta = Usuario.query.filter_by(estatus="A")
    if "searchString" in request.form:
        usuarios_email = safe_email(request.form["searchString"], search_fragment=True)
        if usuarios_email != "":
            consulta = consulta.filter(Usuario.email.contains(usuarios_email))
    resultados = []
    for usuario in consulta.order_by(Usuario.email).limit(20).all():
        resultados.append({"id": usuario.email, "text": usuario.email, "nombre": usuario.nombre})
    return {"results": resultados, "pagination": {"more": False}}


@usuarios.route("/usuarios/select2_json", methods=["POST"])
def select2_json():
    """Proporcionar el JSON de usuarios para elegir con un Select2, se usa para filtrar en DataTables"""
    consulta = Usuario.query.filter(Usuario.estatus == "A")
    if "searchString" in request.form:
        email = safe_email(request.form["searchString"], search_fragment=True)
        if email != "":
            consulta = consulta.filter(Usuario.email.contains(email))
    resultados = []
    for usuario in consulta.order_by(Usuario.email).limit(10).all():
        resultados.append({"id": usuario.id, "text": f"{usuario.email}: {usuario.nombre}"})
    return {"results": resultados, "pagination": {"more": False}}
