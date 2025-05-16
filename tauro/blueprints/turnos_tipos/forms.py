"""
Turnos Tipos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Optional


class TurnoTipoForm(FlaskForm):
    """Formulario TurnoTipo"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    nivel = IntegerField("Nivel", validators=[DataRequired()])
    es_activo = BooleanField("Activo", validators=[Optional()])
    guardar = SubmitField("Guardar")
