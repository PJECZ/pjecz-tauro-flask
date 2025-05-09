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

MODULO = "USUARIOS TURNOS TIPOS"

usuarios_turnos_tipos = Blueprint("usuarios_turnos_tipos", __name__, template_folder="templates")


@usuarios_turnos_tipos.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""
