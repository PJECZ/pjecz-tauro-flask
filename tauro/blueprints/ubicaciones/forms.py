"""
Ubicaciones, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Optional


class UbicacionForm(FlaskForm):
    """Formulario Ubicacion"""

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    numero = IntegerField("Número", validators=[Optional()])
    es_activo = BooleanField("Activa", validators=[Optional()])
    guardar = SubmitField("Guardar")
