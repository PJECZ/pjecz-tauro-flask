"""
API_Keys, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, Length, Optional


class APIKeyForm(FlaskForm):
    """Formulario APIKey"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=128)])
    api_key = StringField("API Key", validators=[DataRequired(), Length(max=128)])
    api_key_expiracion = DateTimeField("Fecha de Expiración", validators=[DataRequired()])
    es_activo = BooleanField("Activo", validators=[Optional()])
    guardar = SubmitField("Guardar")
