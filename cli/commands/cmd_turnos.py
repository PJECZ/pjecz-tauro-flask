"""
CLI Base de Datos
"""

import os
from datetime import datetime
from pytz import timezone

import click
from dotenv import load_dotenv
from sqlalchemy import or_

from tauro.app import create_app
from tauro.extensions import database

from tauro.blueprints.turnos.models import Turno
from tauro.blueprints.turnos_estados.models import TurnoEstado


app = create_app()
app.app_context().push()
database.app = app

load_dotenv()  # Take environment variables from .env
TZ = os.environ.get("TZ", "America/Mexico_City")


@click.group()
def cli():
    """Base de Datos"""


@click.command()
def cancelar_turnos_pasados():
    """Cancelar turnos pasados"""

    # Calcular fecha de hoy
    fecha_hoy = datetime.now(tz=timezone(TZ)).date()
    timestamp_hoy = datetime(
        year=fecha_hoy.year,
        month=fecha_hoy.month,
        day=fecha_hoy.day,
        hour=0,
        minute=0,
        second=0,
    )

    # Definir un contador
    contador = 0

    # Consultar TurnosEstados
    turnos_estados = {turno_estado.nombre: turno_estado for turno_estado in TurnoEstado.query.all()}

    # Consultar turnos anteriores a la fecha de hoy que se encuentren en estado diferente a COMPLETADO.
    turnos = (
        Turno.query.filter(Turno.creado < timestamp_hoy)
        .filter(Turno.turno_estado != turnos_estados["COMPLETADO"])
        .filter(Turno.turno_estado != turnos_estados["CANCELADO"])
        .all()
    )

    # Cambiar el estado de los turnos resultantes a CANCELADO
    for turno in turnos:
        turno.turno_estado = turnos_estados["CANCELADO"]
        turno.save()
        contador += 1

    click.echo(f"{contador} turnos cancelados.")


cli.add_command(cancelar_turnos_pasados)
