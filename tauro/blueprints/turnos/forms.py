"""
Turnos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional

from tauro.blueprints.usuarios.models import Usuario
from tauro.blueprints.unidades.models import Unidad
from tauro.blueprints.ubicaciones.models import Ubicacion
from tauro.blueprints.turnos_tipos.models import TurnoTipo
from tauro.blueprints.turnos_estados.models import TurnoEstado


class TurnoForm(FlaskForm):
    """Formulario Turno"""

    usuario = SelectField("Usuario", coerce=int, validators=[DataRequired()])
    numero = IntegerField("Número", validators=[DataRequired()])
    turnos_tipo = SelectField("Tipo", coerce=int, validators=[DataRequired()])
    unidad = SelectField("Unidad", coerce=int, validators=[DataRequired()])
    ubicacion = SelectField("Ubicacion", coerce=int, validators=[DataRequired()])
    numero_cubiculo = IntegerField("Cubículo", validators=[Optional()])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=20)])
    turnos_estado = SelectField("Estado", coerce=int, validators=[DataRequired()])
    comentarios = TextAreaField("Comentarios", validators=[Optional(), Length(max=512)])

    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones en turnos_tipos"""
        super().__init__(*args, **kwargs)
        self.usuario.choices = [(r.id, r.nombre) for r in Usuario.query.filter_by(estatus="A").order_by(Usuario.nombres).all()]
        self.turnos_tipo.choices = [
            (r.id, r.nombre)
            for r in TurnoTipo.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoTipo.nombre).all()
        ]
        self.unidad.choices = [
            (r.id, r.clave + " - " + r.nombre)
            for r in Unidad.query.filter_by(estatus="A").filter_by(estatus="A").order_by(Unidad.clave).all()
        ]
        self.ubicacion.choices = [
            (v.id, v.nombre + " - " + str(v.numero) if v.numero else "")
            for v in Ubicacion.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(Ubicacion.nombre).all()
        ]
        self.turnos_estado.choices = [
            (e.id, e.nombre)
            for e in TurnoEstado.query.filter_by(estatus="A").filter_by(es_activo=True).order_by(TurnoEstado.nombre).all()
        ]
