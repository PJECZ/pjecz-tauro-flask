"""
Respaldar Unidades
"""

import csv
import sys
from pathlib import Path

import click

from tauro.blueprints.unidades.models import Unidad

UNIDADES_CSV = "seed/unidades.csv"


def respaldar_unidades():
    """Respaldar Unidades"""
    ruta = Path(UNIDADES_CSV)
    if ruta.exists():
        click.echo(f"AVISO: {UNIDADES_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    click.echo("Respaldando Unidades: ", nl=False)
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "unidad_id",
                "clave",
                "nombre",
                "es_activo",
                "estatus",
            ]
        )
        for unidad in Unidad.query.order_by(Unidad.id).all():
            respaldo.writerow(
                [
                    unidad.id,
                    unidad.clave,
                    unidad.nombre,
                    int(unidad.es_activo),
                    unidad.estatus,
                ]
            )
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} unidades respaldadas.", fg="green"))
