"""
Usuarios, vistas
"""

import json
import re
from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from pytz import timezone

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.pwgen import generar_api_key, generar_contrasena
from lib.safe_next_url import safe_next_url
from lib.safe_string import CONTRASENA_REGEXP, EMAIL_REGEXP, TOKEN_REGEXP, safe_email, safe_message, safe_string
from tauro.blueprints.autoridades.models import Autoridad
from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.distritos.models import Distrito
from tauro.blueprints.entradas_salidas.models import EntradaSalida
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import anonymous_required, permission_required
from tauro.blueprints.usuarios.forms import AccesoForm, UsuarioForm
from tauro.blueprints.usuarios.models import Usuario

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
