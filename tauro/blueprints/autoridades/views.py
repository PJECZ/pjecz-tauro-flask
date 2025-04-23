"""
Autoridades, vistas
"""

import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_message, safe_string

# from tauro.blueprints.autoridades.forms import AutoridadEditForm, AutoridadNewForm
from tauro.blueprints.autoridades.models import Autoridad
from tauro.blueprints.bitacoras.models import Bitacora
from tauro.blueprints.distritos.models import Distrito
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import permission_required

MODULO = "AUTORIDADES"

autoridades = Blueprint("autoridades", __name__, template_folder="templates")
