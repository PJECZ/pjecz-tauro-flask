"""
Usuarios, formularios
"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, SelectField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp

from lib.safe_string import CONTRASENA_REGEXP
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.ubicaciones.models import Ubicacion

CONTRASENA_MENSAJE = "De 8 a 48 caracteres con al menos una mayúscula, una minúscula y un número. No acentos, ni eñe."


class AccesoForm(FlaskForm):
    """Formulario de acceso al sistema"""

    siguiente = HiddenField()
    identidad = StringField("Correo electrónico o usuario", validators=[Optional(), Length(8, 256)])
    contrasena = PasswordField(
        "Contraseña",
        validators=[Optional(), Length(8, 48), Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE)],
    )
    email = StringField("Correo electrónico", validators=[Optional(), Email()])
    token = StringField("Token", validators=[Optional()])
    guardar = SubmitField("Guardar")


class UsuarioForm(FlaskForm):
    """Formulario Usuario"""

    email = StringField("e-mail", validators=[DataRequired(), Email()])
    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido primero", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido segundo", validators=[Optional(), Length(max=256)])
    contrasena = PasswordField(
        "Contraseña",
        validators=[Optional(), Length(8, 48), Regexp(CONTRASENA_REGEXP, 0, CONTRASENA_MENSAJE)],
    )
    unidad = SelectField("Unidad", coerce=int, validators=[DataRequired()])
    ubicacion = SelectField("Ubicacion", coerce=int, validators=[Optional()])
    es_acceso_frontend = BooleanField("Acceso al Frontend")
    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones en unidad"""
        super().__init__(*args, **kwargs)
        self.unidad.choices = [
            (u.id, u.clave + ": " + u.nombre)
            for u in Unidad.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(Unidad.clave).all()
        ]
        self.ubicacion.choices = [
            (v.id, v.nombre + " - " + str(v.numero))
            for v in Ubicacion.query.filter_by(estatus="A")
            .filter_by(es_activo=True)
            .order_by(Ubicacion.nombre)
            .order_by(Ubicacion.numero)
            .all()
        ]
