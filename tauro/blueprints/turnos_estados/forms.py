"""
Turnos Estados, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Optional


class TurnoEstadoForm(FlaskForm):
    """Formulario TurnoEstado"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    es_activo = BooleanField("Activo", validators=[Optional()])
    guardar = SubmitField("Guardar")
