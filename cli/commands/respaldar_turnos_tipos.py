"""
Respaldar Turnos_Tipos
"""

import csv
import sys
from pathlib import Path

import click

from tauro.blueprints.turnos_tipos.models import TurnoTipo

TURNOS_TIPOS_CSV = "seed/turnos_tipos.csv"


def respaldar_turnos_tipos():
    """Respaldar Turnos_Tipos"""
    ruta = Path(TURNOS_TIPOS_CSV)
    if ruta.exists():
        click.echo(f"AVISO: {TURNOS_TIPOS_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    click.echo("Respaldando Turnos-Tipos: ", nl=False)
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "turno_tipo_id",
                "nombre",
                "es_activo",
                "estatus",
            ]
        )
        for turno_tipo in TurnoTipo.query.order_by(TurnoTipo.id).all():
            respaldo.writerow(
                [
                    turno_tipo.id,
                    turno_tipo.nombre,
                    int(turno_tipo.es_activo),
                    turno_tipo.estatus,
                ]
            )
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} turnos-tipos respaldados.", fg="green"))
