"""
Respaldar Turnos_Estados
"""

import csv
import sys
from pathlib import Path

import click

from tauro.blueprints.turnos_estados.models import Turno_Estado

TURNOS_ESTADOS_CSV = "seed/turnos_estados.csv"


def respaldar_turnos_estados():
    """Respaldar Turnos_Estados"""
    ruta = Path(TURNOS_ESTADOS_CSV)
    if ruta.exists():
        click.echo(f"AVISO: {TURNOS_ESTADOS_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    click.echo("Respaldando Turnos-Estados: ", nl=False)
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "turno_estado_id",
                "nombre",
                "es_activo",
                "estatus",
            ]
        )
        for turno_estado in Turno_Estado.query.order_by(Turno_Estado.id).all():
            respaldo.writerow(
                [
                    turno_estado.id,
                    turno_estado.nombre,
                    int(turno_estado.es_activo),
                    turno_estado.estatus,
                ]
            )
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} turnos-estados respaldados.", fg="green"))
