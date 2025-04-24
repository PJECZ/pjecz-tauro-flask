"""
Ventanillas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class VentanillaForm(FlaskForm):
    """Formulario Ventanilla"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")
