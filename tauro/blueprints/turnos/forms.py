"""
Turnos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from tauro.blueprints.turnos.models import Turno


class TurnoForm(FlaskForm):
    """Formulario Turno"""

    tipo = SelectField("Tipo", choices=Turno.TIPOS.items(), validators=[DataRequired(), Length(max=16)])
    comentarios = TextAreaField("Comentarios", validators=[Optional(), Length(max=512)])
    guardar = SubmitField("Guardar")
