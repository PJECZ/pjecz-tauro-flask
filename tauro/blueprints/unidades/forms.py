"""
Unidades, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Optional


class UnidadForm(FlaskForm):
    """Formulario Unidad"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    pronunciacion = StringField("Pronunciación", validators=[Optional(), Length(max=32)])
    es_activo = BooleanField("Activo", validators=[Optional()])
    guardar = SubmitField("Guardar")
