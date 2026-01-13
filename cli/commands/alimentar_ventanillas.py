"""
Alimentar Ubicaciones
"""

import csv
import sys
from pathlib import Path

import click

from lib.safe_string import safe_string
from tauro.blueprints.ubicaciones.models import Ubicacion

UBICAIONES_CSV = "seed/ubicaciones.csv"


def alimentar_ubicaciones():
    """Alimentar Ubicaciones"""
    ruta_csv = Path(UBICAIONES_CSV)
    if not ruta_csv.exists():
        click.echo(f"AVISO: {ruta_csv.name} no se encontró.")
        sys.exit(1)
    if not ruta_csv.is_file():
        click.echo(f"AVISO: {ruta_csv.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando ubicaciones: ", nl=False)
    contador = 0
    with open(ruta_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            ubicacion_id = int(row["ubicacion_id"])
            nombre = safe_string(row["nombre"], save_enie=True)
            numero = row["numero"]
            if numero == "":
                numero = None
            es_activo = row["es_activo"] == "1"
            estatus = row["estatus"]
            if ubicacion_id != contador + 1:
                click.echo(click.style(f"  AVISO: ubicacion_id {ubicacion_id} no es consecutivo", fg="red"))
                sys.exit(1)
            Ubicacion(
                nombre=nombre,
                numero=numero,
                es_activo=es_activo,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} ubicaciones alimentadas.", fg="green"))
