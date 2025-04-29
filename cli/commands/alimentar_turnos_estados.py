"""
Alimentar Turnos_Estados
"""

import csv
import sys
from pathlib import Path

import click

from lib.safe_string import safe_string
from tauro.blueprints.turnos_estados.models import Turno_Estado

TURNOS_ESTADOS_CSV = "seed/turnos_estados.csv"


def alimentar_turnos_estados():
    """Alimentar Turnos-Estados"""
    ruta_csv = Path(TURNOS_ESTADOS_CSV)
    if not ruta_csv.exists():
        click.echo(f"AVISO: {ruta_csv.name} no se encontró.")
        sys.exit(1)
    if not ruta_csv.is_file():
        click.echo(f"AVISO: {ruta_csv.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando turnos_estados: ", nl=False)
    contador = 0
    with open(ruta_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            turno_estado_id = int(row["turno_estado_id"])
            nombre = safe_string(row["nombre"], save_enie=True)
            es_activo = row["es_activo"] == "1"
            estatus = row["estatus"]
            if turno_estado_id != contador + 1:
                click.echo(click.style(f"  AVISO: turno_estado_id {turno_estado_id} no es consecutivo", fg="red"))
                sys.exit(1)
            Turno_Estado(
                nombre=nombre,
                es_activo=es_activo,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} turnos_estados alimentados.", fg="green"))
