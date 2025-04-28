"""
Ventanillas, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from tauro.blueprints.unidades.models import Unidad


class VentanillaForm(FlaskForm):
    """Formulario Ventanilla"""

    clave = StringField("Clave", validators=[DataRequired(), Length(max=16)])
    unidad = SelectField("Unidad", coerce=int, validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[Optional(), Length(max=256)])
    es_habilitada = BooleanField("Habilitada", validators=[Optional()])
    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones para unidades"""
        super().__init__(*args, **kwargs)
        self.unidad.choices = [
            (u.id, u.clave + " - " + u.nombre) for u in Unidad.query.filter_by(estatus="A").order_by(Unidad.clave).all()
        ]
