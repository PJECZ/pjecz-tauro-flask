"""
Turnos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from tauro.blueprints.turnos_tipos.models import TurnoTipo


class TurnoForm(FlaskForm):
    """Formulario Turno"""

    turno_tipo = SelectField("Tipo", coerce=int, validators=[DataRequired()])
    comentarios = TextAreaField("Comentarios", validators=[Optional(), Length(max=512)])
    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones en turnos_tipos"""
        super().__init__(*args, **kwargs)
        self.turno_tipo.choices = [
            (r.id, r.nombre)
            for r in TurnoTipo.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoTipo.nombre).all()
        ]
