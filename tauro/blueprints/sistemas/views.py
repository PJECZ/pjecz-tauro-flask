"""
Sistemas
"""

import locale
from datetime import datetime

from flask import Blueprint, redirect, render_template, send_from_directory, url_for, flash
from flask_login import current_user

from tauro.extensions import socketio
from tauro.blueprints.api_v1.schemas import ResponseSchema
from tauro.services.vocear_turnos import VocearTurnos

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
        data={"signal": True},
    ).model_dump()

    # Enviar mensaje vía socketio a todos los clientes conectados
    socketio.emit("refresh_screens", response_refresh)

    flash("Señal enviada correctamente, espere a que se actualicen las pantallas de turnos.", "success")
    return redirect(url_for(("sistemas.start")))


@sistemas.route("/test_voceador")
def test_voceador():
    """Envía señal de test a la API del sistema Voceador"""

    # Crear conexión con el servicio de voceo
    voceador_turnos = VocearTurnos()
    locale.setlocale(locale.LC_TIME, "es_MX.utf8")
    mensaje_de_prueba = f"¡ATENCIÓN!, Prueba de sonido: 1, 2, 3. Bienvenido a la Ciudad Judicial de Saltillo, el día de hoy es {datetime.now().strftime('%-d de %B del %Y')}. Que tengan un buen día, gracias."
    try:
        resultado, mensaje_resp = voceador_turnos.probar_sonido(mensaje_de_prueba)
    except Exception:
        pass

    # Mensaje de respuesta
    if resultado:
        flash("Señal enviada correctamente, debería escuchar un mensaje de prueba en el sistema voceador.", "success")
    else:
        flash(f"ADVERTENCIA: Ocurrió un error con el servicio voceador. {mensaje_resp}", "warning")
    # Muestra la respuesta
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
