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

# from tauro.blueprints.entradas_salidas.models import EntradaSalida
from tauro.blueprints.modulos.models import Modulo
from tauro.blueprints.permisos.models import Permiso
from tauro.blueprints.usuarios.decorators import anonymous_required, permission_required

# from tauro.blueprints.usuarios.forms import AccesoForm, UsuarioForm
from tauro.blueprints.usuarios.models import Usuario

MODULO = "USUARIOS"

usuarios = Blueprint("usuarios", __name__, template_folder="templates")
