"""
Usuario-Turnos_Tipos: Clase, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from tauro.blueprints.turnos_tipos.models import TurnoTipo


class UsuarioTurnoTipoForm(FlaskForm):
    """Formulario UsuarioTurnoTipo"""

    usuario = StringField("Usuario")
    turno_tipo = SelectField("Turno Tipo", coerce=int, validators=[DataRequired()])
    es_activo = BooleanField("Activo", validators=[Optional()])
    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones en turnos-tipos"""
        super().__init__(*args, **kwargs)
        self.turno_tipo.choices = [
            (tt.id, tt.nombre)
            for tt in TurnoTipo.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoTipo.nombre).all()
        ]
