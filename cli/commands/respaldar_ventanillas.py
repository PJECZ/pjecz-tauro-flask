"""
Respaldar Ventanillas
"""

import csv
import sys
from pathlib import Path

import click

from tauro.blueprints.ventanillas.models import Ventanilla

VENTANILLAS_CSV = "seed/ventanillas.csv"


def respaldar_ventanillas():
    """Respaldar Ventanillas"""
    ruta = Path(VENTANILLAS_CSV)
    if ruta.exists():
        click.echo(f"AVISO: {VENTANILLAS_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    click.echo("Respaldando Ventanillas: ", nl=False)
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "ventanilla_id",
                "nombre",
                "es_activo",
                "estatus",
            ]
        )
        for ventanilla in Ventanilla.query.order_by(Ventanilla.id).all():
            respaldo.writerow(
                [
                    ventanilla.id,
                    ventanilla.nombre,
                    int(ventanilla.es_activo),
                    ventanilla.estatus,
                ]
            )
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} ventanillas respaldadas.", fg="green"))
