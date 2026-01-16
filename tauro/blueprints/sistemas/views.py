"""
Sistemas
"""

from flask import Blueprint, redirect, render_template, send_from_directory, url_for, flash
from flask_login import current_user

from tauro.extensions import socketio
from tauro.blueprints.api_v1.schemas import ResponseSchema

sistemas = Blueprint("sistemas", __name__, template_folder="templates")


@sistemas.route("/")
def start():
    """Pagina Inicial"""

    # Si el usuario está autenticado, mostrar start.jinja2
    if current_user.is_authenticated:
        return render_template("sistemas/start.jinja2")

    # No está autenticado, debe de iniciar sesión
    return redirect(url_for("usuarios.login"))


@sistemas.route("/refresh_screens")
def refresh_screens():
    """Envía señal vía socketio para refrescar las pantallas"""

    # Crear estructura de respuesta
    response_refresh = ResponseSchema(
        success=True,
        message="Señal de actualización de pantallas",
        data={"signal": "refresh"},
    ).model_dump()

    # Enviar mensaje vía socketio
    socketio.send(response_refresh)

    flash("Señal enviada correctamente, espere a que se actualicen las pantallas de turnos.", "success")
    return redirect(url_for(("sistemas.start")))


@sistemas.route("/favicon.ico")
def favicon():
    """Favicon"""
    return send_from_directory("static/img", "favicon.ico", mimetype="image/vnd.microsoft.icon")


@sistemas.app_errorhandler(400)
def bad_request(error):
    """Solicitud errónea"""
    return render_template("sistemas/403.jinja2", error=error), 403


@sistemas.app_errorhandler(403)
def forbidden(error):
    """Acceso no autorizado"""
    return render_template("sistemas/403.jinja2"), 403


@sistemas.app_errorhandler(404)
def page_not_found(error):
    """Error página no encontrada"""
    return render_template("sistemas/404.jinja2"), 404


@sistemas.app_errorhandler(500)
def internal_server_error(error):
    """Error del servidor"""
    return render_template("sistemas/500.jinja2"), 500
