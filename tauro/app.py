"""
Flask App
"""

from flask import Flask

from config.settings import Settings
from tauro.blueprints.bitacoras.views import bitacoras
from tauro.blueprints.entradas_salidas.views import entradas_salidas
from tauro.blueprints.modulos.views import modulos
from tauro.blueprints.permisos.views import permisos
from tauro.blueprints.roles.views import roles
from tauro.blueprints.sistemas.views import sistemas
from tauro.blueprints.turnos.views import turnos
from tauro.blueprints.turnos_estados.views import turnos_estados
from tauro.blueprints.turnos_tipos.views import turnos_tipos
from tauro.blueprints.unidades.views import unidades
from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.usuarios.views import usuarios
from tauro.blueprints.usuarios_roles.views import usuarios_roles
from tauro.blueprints.ventanillas.views import ventanillas
from tauro.extensions import csrf, database, login_manager, moment


def create_app():
    """Crear app"""
    # Definir app
    app = Flask(__name__, instance_relative_config=True)

    # Cargar la configuración
    app.config.from_object(Settings())

    # Registrar blueprints
    app.register_blueprint(bitacoras)
    app.register_blueprint(entradas_salidas)
    app.register_blueprint(modulos)
    app.register_blueprint(permisos)
    app.register_blueprint(roles)
    app.register_blueprint(sistemas)
    app.register_blueprint(turnos)
    app.register_blueprint(turnos_estados)
    app.register_blueprint(turnos_tipos)
    app.register_blueprint(unidades)
    app.register_blueprint(usuarios)
    app.register_blueprint(usuarios_roles)
    app.register_blueprint(ventanillas)

    # Inicializar extensiones
    extensions(app)

    # Inicializar autenticación
    authentication(Usuario)

    # Entregar app
    return app


def extensions(app):
    """Inicializar extensiones"""
    csrf.init_app(app)
    database.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    # socketio.init_app(app)


def authentication(user_model):
    """Inicializar Flask-Login"""
    login_manager.login_view = "usuarios.login"

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)
