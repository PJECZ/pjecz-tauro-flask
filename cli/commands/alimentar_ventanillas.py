"""
Alimentar Ventanillas
"""

import csv
import sys
from pathlib import Path

import click

from lib.safe_string import safe_string
from tauro.blueprints.ventanillas.models import Ventanilla

VENTANILLAS_CSV = "seed/ventanillas.csv"


def alimentar_ventanillas():
    """Alimentar Ventanillas"""
    ruta_csv = Path(VENTANILLAS_CSV)
    if not ruta_csv.exists():
        click.echo(f"AVISO: {ruta_csv.name} no se encontró.")
        sys.exit(1)
    if not ruta_csv.is_file():
        click.echo(f"AVISO: {ruta_csv.name} no es un archivo.")
        sys.exit(1)
    click.echo("Alimentando ventanillas: ", nl=False)
    contador = 0
    with open(ruta_csv, encoding="utf8") as puntero:
        rows = csv.DictReader(puntero)
        for row in rows:
            ventanilla_id = int(row["ventanilla_id"])
            nombre = safe_string(row["nombre"], save_enie=True)
            numero = row["numero"]
            es_activo = row["es_activo"] == "1"
            estatus = row["estatus"]
            if ventanilla_id != contador + 1:
                click.echo(click.style(f"  AVISO: ventanilla_id {ventanilla_id} no es consecutivo", fg="red"))
                sys.exit(1)
            Ventanilla(
                nombre=nombre,
                numero=numero,
                es_activo=es_activo,
                estatus=estatus,
            ).save()
            contador += 1
            click.echo(click.style(".", fg="green"), nl=False)
    click.echo()
    click.echo(click.style(f"  {contador} ventanillas alimentadas.", fg="green"))
