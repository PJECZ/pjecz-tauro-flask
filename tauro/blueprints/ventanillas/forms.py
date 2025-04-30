"""
Ventanillas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional


class VentanillaForm(FlaskForm):
    """Formulario Ventanilla"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    es_activo = BooleanField("Activa", validators=[Optional()])
    guardar = SubmitField("Guardar")
