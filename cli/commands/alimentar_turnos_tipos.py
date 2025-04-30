"""
Alimentar Turnos_Tipos
"""

import csv
import sys
from pathlib import Path

import click

from lib.safe_string import safe_string
from tauro.blueprints.turnos_tipos.models import TurnoTipo

TURNOS_TIPOS_CSV = "seed/turnos_tipos.csv"


def alimentar_turnos_tipos():
    """Alimentar Turnos-Tipos"""
    ruta_csv = Path(TURNOS_TIPOS_CSV)
    if not ruta_csv.exists():
        click.echo(f"AVISO: {ruta_csv.name} no se encontró.")
        sys.exit(1)
    if not ruta_csv.is_file():
        click.echo(f"AVISO: {ruta_csv.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando turnos_tipos: ", nl=False)
    contador = 0
    with open(ruta_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            turno_tipo_id = int(row["turno_tipo_id"])
            nombre = safe_string(row["nombre"], save_enie=True)
            es_activo = row["es_activo"] == "1"
            estatus = row["estatus"]
            if turno_tipo_id != contador + 1:
                click.echo(click.style(f"  AVISO: turno_tipo_id {turno_tipo_id} no es consecutivo", fg="red"))
                sys.exit(1)
            TurnoTipo(
                nombre=nombre,
                es_activo=es_activo,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} turnos_tipos alimentados.", fg="green"))
