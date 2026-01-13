"""
Respaldar Ubicaciones
"""

import csv
import sys
from pathlib import Path

import click

from tauro.blueprints.ubicaciones.models import Ubicacion

UBICACIONES_CSV = "seed/ubicaciones.csv"


def respaldar_ubicaciones():
    """Respaldar Ubicaciones"""
    ruta = Path(UBICACIONES_CSV)
    if ruta.exists():
        click.echo(f"AVISO: {UBICACIONES_CSV} ya existe, no voy a sobreescribirlo.")
        sys.exit(1)
    click.echo("Respaldando Ubicaciones: ", nl=False)
    contador = 0
    with open(ruta, "w", encoding="utf8") as puntero:
        respaldo = csv.writer(puntero)
        respaldo.writerow(
            [
                "ubicacion_id",
                "nombre",
                "numero",
                "es_activo",
                "estatus",
            ]
        )
        for ubicacion in Ubicacion.query.order_by(Ubicacion.id).all():
            respaldo.writerow(
                [
                    ubicacion.id,
                    ubicacion.nombre,
                    ubicacion.numero,
                    int(ubicacion.es_activo),
                    ubicacion.estatus,
                ]
            )
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} ubicaciones respaldadas.", fg="green"))
